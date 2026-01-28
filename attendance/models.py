from calendar import monthrange
from datetime import date, datetime, time, timedelta
from typing import Optional

from django.conf import settings
from django.db import models
from django.db.models import Sum
from django.utils import timezone


class AttendanceRule(models.Model):
    """Singleton model storing organisation-wide attendance rules."""

    work_start = models.TimeField(default=time(9, 0))
    work_end = models.TimeField(default=time(17, 30))
    grace_minutes = models.PositiveIntegerField(default=5)
    standard_work_minutes = models.PositiveIntegerField(default=510)  # 8h30m
    overtime_after_minutes = models.PositiveIntegerField(default=510)
    late_penalty_per_minute = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    per_day_deduction = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    overtime_rate_per_minute = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    weekend_days = models.JSONField(default=list, blank=True)
    min_break_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Flag breaks shorter than this duration (minutes). Leave blank to disable.",
    )
    max_break_minutes = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Flag breaks longer than this duration (minutes). Leave blank to disable.",
    )
    grace_violation_deduction = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Fixed deduction amount when employee checks in after grace period"
    )
    early_checkout_threshold_minutes = models.PositiveIntegerField(
        default=20,
        help_text="Threshold in minutes before work_end to consider check-out as early"
    )
    early_checkout_deduction = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        help_text="Fixed deduction amount for early check-out"
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Attendance rule'
        verbose_name_plural = 'Attendance rules'

    def save(self, *args, **kwargs):
        if not self.weekend_days:
            self.weekend_days = [5, 6]
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        instance = cls.objects.first()
        if instance:
            return instance
        instance = cls.objects.create()
        return instance

    @classmethod
    def get_holidays_for_month(cls, year: int, month: int):
        """Retrieve all holidays for a specific month."""
        return Holiday.objects.filter(date__year=year, date__month=month)

    def calculate_ideal_monthly_hours(self, year: int, month: int) -> dict:
        """
        Calculate ideal monthly working hours excluding weekends and holidays.
        All calculations are rounded to 2 decimal places per step.
        
        Args:
            year: Year for calculation
            month: Month for calculation (1-12)
            
        Returns:
            dict with:
                - ideal_monthly_hours: Total ideal hours (rounded to 2 decimals)
                - working_days: Count of working days
                - weekend_days: Count of weekend days
                - holidays: Count of holidays
                - holiday_list: List of holiday dates and names
                - standard_work_hours_per_day: Hours per day (rounded to 2 decimals)
        """
        # Get all days in the month
        start = date(year, month, 1)
        end = date(year, month, monthrange(year, month)[1])
        
        # Get weekend days (JavaScript format: 0=Sunday, 1=Monday, ..., 6=Saturday)
        weekend_days_set = set(int(d) for d in (self.weekend_days or []))
        
        # Get holidays for the month
        holidays = self.get_holidays_for_month(year, month)
        holiday_dates = {h.date for h in holidays}
        
        # Count working days, weekends, and holidays
        working_days = 0
        weekend_count = 0
        cur = start
        while cur <= end:
            # Convert Python weekday (0=Monday, 6=Sunday) to JavaScript weekday (0=Sunday, 6=Saturday)
            js_weekday = (cur.weekday() + 1) % 7
            if js_weekday in weekend_days_set:
                weekend_count += 1
            elif cur in holiday_dates:
                # Holiday (already counted, but not as working day)
                pass
            else:
                working_days += 1
            cur += timedelta(days=1)
        
        # Calculate standard work hours per day (rounded to 2 decimals)
        standard_work_hours_per_day = round(self.standard_work_minutes / 60, 2)
        
        # Calculate ideal monthly hours (rounded to 2 decimals)
        ideal_monthly_hours = round(working_days * standard_work_hours_per_day, 2)
        
        # Prepare holiday list
        holiday_list = [
            {'date': str(h.date), 'name': h.name}
            for h in holidays.order_by('date')
        ]
        
        return {
            'ideal_monthly_hours': ideal_monthly_hours,
            'working_days': working_days,
            'weekend_days': weekend_count,
            'holidays': len(holiday_dates),
            'holiday_list': holiday_list,
            'standard_work_hours_per_day': standard_work_hours_per_day,
        }


class Holiday(models.Model):
    """Model to store public holidays."""
    
    date = models.DateField(unique=True, help_text="Date of the holiday")
    name = models.CharField(max_length=255, help_text="Name/description of the holiday")
    is_recurring = models.BooleanField(
        default=False,
        help_text="Whether this holiday recurs annually (for future use)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Holiday'
        verbose_name_plural = 'Holidays'
        ordering = ['date']
    
    def __str__(self):
        return f"{self.name} ({self.date})"


class Attendance(models.Model):
    STATUS_PRESENT = 'present'
    STATUS_LATE = 'late'
    STATUS_ABSENT = 'absent'
    STATUS_CHOICES = (
        (STATUS_PRESENT, 'Present'),
        (STATUS_LATE, 'Late'),
        (STATUS_ABSENT, 'Absent'),
    )

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendance_records')
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(null=True, blank=True)
    date = models.DateField()
    total_hours = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PRESENT)
    location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_address = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    device_id = models.CharField(max_length=255, blank=True)
    device_info = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_break_minutes = models.PositiveIntegerField(default=0)
    effective_minutes = models.PositiveIntegerField(default=0)
    overtime_minutes = models.PositiveIntegerField(default=0)
    overtime_verified = models.BooleanField(default=False)
    overtime_verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_overtime_records',
    )
    overtime_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-date', '-check_in']

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

    def save(self, *args, **kwargs):
        if self.check_in and not self.date:
            self.date = timezone.localdate(self.check_in)

        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            total_minutes = max(int(duration.total_seconds() // 60), 0)
            self.total_hours = round(total_minutes / 60, 2)
            self._recalculate_breaks(total_minutes=total_minutes)
        else:
            self.total_hours = None
            self.total_break_minutes = 0
            self.effective_minutes = 0
        super().save(*args, **kwargs)

    @property
    def duration_display(self) -> str:
        if not self.check_out:
            return 'In Progress'
        duration = self.check_out - self.check_in
        total_minutes = int(duration.total_seconds() // 60)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours}h {minutes}m"

    @classmethod
    def determine_status(cls, check_in_dt: datetime) -> str:
        rules = AttendanceRule.get_solo()
        tz = timezone.get_current_timezone()
        local_dt = timezone.localtime(check_in_dt)
        start_dt = timezone.make_aware(datetime.combine(local_dt.date(), rules.work_start), tz)
        grace_delta = timedelta(minutes=rules.grace_minutes)
        if local_dt > start_dt + grace_delta:
            return cls.STATUS_LATE
        return cls.STATUS_PRESENT

    def _recalculate_breaks(self, *, total_minutes: Optional[int] = None, save: bool = False) -> None:
        """
        Update cached break and effective minute totals.

        Args:
            total_minutes: Optional precomputed total working minutes between check-in/out.
            save: Persist the model after recalculation when True.
        """
        if total_minutes is None and self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            total_minutes = max(int(duration.total_seconds() // 60), 0)

        # Only access breaks if instance has a primary key (is saved)
        if self.pk:
            break_minutes = (
                self.breaks.aggregate(total=Sum('duration_minutes'))['total'] or 0
            )
        else:
            break_minutes = 0
        self.total_break_minutes = max(int(break_minutes), 0)

        if total_minutes is None:
            effective = 0
        else:
            effective = max(total_minutes - self.total_break_minutes, 0)
        self.effective_minutes = effective

        if total_minutes is not None:
            self.total_hours = round(total_minutes / 60, 2)

        # Recalculate overtime when effective minutes change
        if self.check_out:  # Only calculate overtime if checked out
            self.calculate_overtime(save=False)

        if save:
            update_fields = ['total_hours', 'total_break_minutes', 'effective_minutes', 'overtime_minutes', 'updated_at']
            super().save(update_fields=update_fields)

    @property
    def active_break(self) -> Optional['AttendanceBreak']:
        return self.breaks.filter(ended_at__isnull=True).order_by('-started_at').first()

    @property
    def has_active_break(self) -> bool:
        return self.active_break is not None

    @property
    def effective_hours(self) -> float:
        return round(self.effective_minutes / 60, 2) if self.effective_minutes else 0.0

    @property
    def is_monitored(self) -> bool:
        """Check if attendance was logged via monitoring system."""
        return bool(self.device_id or self.device_name)

    def calculate_overtime(self, save: bool = False) -> int:
        """
        Calculate overtime minutes based on effective working hours minus standard working hours.
        Only counts overtime if attendance was logged via monitoring system.
        
        Args:
            save: If True, save the model after calculating overtime.
            
        Returns:
            Overtime minutes (0 if not monitored or negative).
        """
        if not self.is_monitored:
            self.overtime_minutes = 0
            if save:
                super().save(update_fields=['overtime_minutes', 'updated_at'])
            return 0
        
        try:
            rules = AttendanceRule.get_solo()
            standard_minutes = rules.standard_work_minutes
        except Exception:
            standard_minutes = 510  # Default fallback
        
        # Calculate: overtime = max(0, effective_minutes - standard_work_minutes)
        overtime = max(0, self.effective_minutes - standard_minutes)
        self.overtime_minutes = overtime
        
        # Note: Don't automatically set overtime_verified to False if overtime > threshold
        # This should only be set by admin verification
        
        if save:
            update_fields = ['overtime_minutes', 'updated_at']
            super().save(update_fields=update_fields)
        
        return overtime

    @property
    def overtime_hours(self) -> float:
        """Return overtime in hours. Safely handles missing column."""
        try:
            overtime_minutes = getattr(self, 'overtime_minutes', 0)
            return round(overtime_minutes / 60, 2) if overtime_minutes else 0.0
        except (AttributeError, ValueError):
            return 0.0

    @property
    def requires_verification(self) -> bool:
        """Check if overtime requires admin verification (overtime > 4 hours). Safely handles missing columns."""
        try:
            overtime_minutes = getattr(self, 'overtime_minutes', 0)
            overtime_verified = getattr(self, 'overtime_verified', False)
            return overtime_minutes > 240 and not overtime_verified
        except (AttributeError, ValueError):
            return False


class AttendanceBreak(models.Model):
    SOURCE_WEB = 'web'
    SOURCE_AGENT = 'agent'
    SOURCE_CHOICES = (
        (SOURCE_WEB, 'Web'),
        (SOURCE_AGENT, 'Agent'),
    )

    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='breaks')
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_WEB)
    notes = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        status = 'active' if self.is_active else 'completed'
        return f"Break ({status}) for {self.attendance}"

    @property
    def is_active(self) -> bool:
        return self.ended_at is None

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.ended_at and self.ended_at < self.started_at:
            raise ValidationError('Break end time cannot be before start time.')

    def _compute_duration_minutes(self) -> int:
        if not self.started_at:
            return 0
        end = self.ended_at or timezone.now()
        return max(int((end - self.started_at).total_seconds() // 60), 0)

    @property
    def current_duration_minutes(self) -> int:
        return self._compute_duration_minutes()

    def end_break(self, ended_at: Optional[datetime] = None, metadata: Optional[dict] = None) -> None:
        if not ended_at:
            ended_at = timezone.now()
        self.ended_at = ended_at
        self.duration_minutes = self._compute_duration_minutes()
        flag_reasons: list[str] = []
        try:
            rules = AttendanceRule.get_solo()
        except Exception:
            rules = None

        if rules:
            min_break = getattr(rules, 'min_break_minutes', None)
            max_break = getattr(rules, 'max_break_minutes', None)
            if min_break is not None and min_break > 0 and self.duration_minutes < min_break:
                flag_reasons.append(f"Short break ({self.duration_minutes} min < {min_break} min)")
            if max_break is not None and max_break > 0 and self.duration_minutes > max_break:
                flag_reasons.append(f"Long break ({self.duration_minutes} min > {max_break} min)")

        if flag_reasons:
            self.is_flagged = True
            self.flag_reason = "; ".join(flag_reasons)[:255]
        else:
            self.is_flagged = False
            self.flag_reason = ""

        if metadata:
            self.metadata.update(metadata)
        self.save()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if self.ended_at:
            self.duration_minutes = self._compute_duration_minutes()
        super().save(*args, **kwargs)
        # Recalculate totals for parent attendance when break changes
        self.attendance._recalculate_breaks(save=True)


class LeaveRequest(models.Model):
    """Model for employee leave requests."""
    
    LEAVE_TYPE_FULL_DAY = 'full_day'
    LEAVE_TYPE_PARTIAL_DAY = 'partial_day'
    LEAVE_TYPE_MULTIPLE_DAYS = 'multiple_days'
    LEAVE_TYPE_CHOICES = (
        (LEAVE_TYPE_FULL_DAY, 'Full Day'),
        (LEAVE_TYPE_PARTIAL_DAY, 'Partial Day'),
        (LEAVE_TYPE_MULTIPLE_DAYS, 'Multiple Days'),
    )
    
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    )
    
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True, help_text="Required for multiple days, optional for single day")
    start_time = models.TimeField(null=True, blank=True, help_text="Required for partial-day leave")
    end_time = models.TimeField(null=True, blank=True, help_text="Optional for partial-day leave")
    hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Leave hours for partial-day leave"
    )
    reason = models.TextField(help_text="Mandatory reason for leave")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    is_paid = models.BooleanField(default=False, help_text="Whether this leave is paid (set by admin)")
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_leave_requests'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['employee', 'status'], name='attendance__employe_a2f1b5_idx'),
            models.Index(fields=['start_date', 'end_date'], name='attendance__start_d_5c073b_idx'),
            models.Index(fields=['status'], name='attendance__status_6e3dfd_idx'),
        ]
    
    def __str__(self):
        return f"{self.employee.username} - {self.get_leave_type_display()} - {self.start_date}"
    
    def get_total_hours(self) -> float:
        """
        Calculate total leave hours.
        - Full day: standard_work_minutes / 60
        - Multiple days: (number of working days) * (standard_work_minutes / 60)
        - Partial day: hours field or calculated from start_time/end_time
        """
        try:
            rules = AttendanceRule.get_solo()
            standard_hours_per_day = rules.standard_work_minutes / 60
        except Exception:
            standard_hours_per_day = 8.5  # Default fallback
        
        if self.leave_type == self.LEAVE_TYPE_PARTIAL_DAY:
            if self.hours:
                return float(self.hours)
            elif self.start_time and self.end_time:
                # Calculate hours from time range
                start_minutes = self.start_time.hour * 60 + self.start_time.minute
                end_minutes = self.end_time.hour * 60 + self.end_time.minute
                if end_minutes < start_minutes:
                    # Handle overnight (shouldn't happen for partial day, but handle gracefully)
                    end_minutes += 24 * 60
                total_minutes = end_minutes - start_minutes
                return round(total_minutes / 60, 2)
            else:
                return 0.0
        
        elif self.leave_type == self.LEAVE_TYPE_FULL_DAY:
            return round(standard_hours_per_day, 2)
        
        elif self.leave_type == self.LEAVE_TYPE_MULTIPLE_DAYS:
            if not self.end_date:
                return round(standard_hours_per_day, 2)
            
            # Count working days (excluding weekends and holidays)
            weekend_days_set = set()
            try:
                rules = AttendanceRule.get_solo()
                weekend_days_set = set(int(d) for d in (rules.weekend_days or []))
            except Exception:
                pass
            
            holidays = Holiday.objects.filter(
                date__gte=self.start_date,
                date__lte=self.end_date
            )
            holiday_dates = {h.date for h in holidays}
            
            working_days = 0
            cur = self.start_date
            while cur <= self.end_date:
                js_weekday = (cur.weekday() + 1) % 7
                if js_weekday not in weekend_days_set and cur not in holiday_dates:
                    working_days += 1
                cur += timedelta(days=1)
            
            return round(working_days * standard_hours_per_day, 2)
        
        return 0.0
    
    def has_conflict(self) -> bool:
        """Check if this leave request conflicts with existing approved/pending leaves for the same employee."""
        if not self.pk:
            # New request - check against all existing leaves
            conflicting = self.get_conflicting_leaves()
        else:
            # Existing request - check against other leaves (excluding self)
            conflicting = self.get_conflicting_leaves().exclude(pk=self.pk)
        return conflicting.exists()
    
    def get_conflicting_leaves(self):
        """
        Return queryset of conflicting leave requests for the same employee.
        Conflicts occur when date ranges overlap.
        """
        if not self.start_date:
            return LeaveRequest.objects.none()
        
        # Determine the effective end date
        effective_end_date = self.end_date if self.end_date else self.start_date
        
        # For partial-day leaves, we need to check if they're on the same day
        # For now, we'll consider any leave on the same day as a conflict
        # This can be refined later to check time ranges
        
        # Query for overlapping leaves (same employee, pending or approved status)
        overlapping = LeaveRequest.objects.filter(
            employee=self.employee,
            status__in=[self.STATUS_PENDING, self.STATUS_APPROVED]
        ).filter(
            # Leave starts before or on our end date AND ends after or on our start date
            start_date__lte=effective_end_date
        ).filter(
            models.Q(end_date__gte=self.start_date) | models.Q(end_date__isnull=True, start_date__gte=self.start_date)
        )
        
        return overlapping
    
    def clean(self):
        """Validate the leave request."""
        from django.core.exceptions import ValidationError
        
        # Validate end_date for multiple days
        if self.leave_type == self.LEAVE_TYPE_MULTIPLE_DAYS and not self.end_date:
            raise ValidationError('End date is required for multiple days leave.')
        
        # Validate end_date is after start_date
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError('End date cannot be before start date.')
        
        # Validate partial-day fields
        if self.leave_type == self.LEAVE_TYPE_PARTIAL_DAY:
            if not self.start_time and not self.hours:
                raise ValidationError('Either start_time/end_time or hours must be provided for partial-day leave.')
            if self.start_time and self.end_time and self.end_time < self.start_time:
                raise ValidationError('End time cannot be before start time.')
        
        # Validate reason is provided
        if not self.reason or not self.reason.strip():
            raise ValidationError('Reason is mandatory for leave requests.')
    
    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.clean()
        super().save(*args, **kwargs)
