"""
Unit tests for clients models.
"""
import pytest
from clients.models import Organization, Contact, Lead, Client
from tests.factories import (
    OrganizationFactory, ContactFactory, LeadFactory, ClientFactory, UserFactory
)


@pytest.mark.django_db
@pytest.mark.unit
class TestOrganizationModel:
    """Test Organization model."""
    
    def test_organization_creation(self):
        """Test basic organization creation."""
        org = OrganizationFactory()
        assert org.name is not None
        assert str(org) == org.name
    
    def test_organization_string_representation(self):
        """Test organization string representation."""
        org = OrganizationFactory(name='Test Company')
        assert str(org) == 'Test Company'


@pytest.mark.django_db
@pytest.mark.unit
class TestContactModel:
    """Test Contact model."""
    
    def test_contact_creation(self):
        """Test basic contact creation."""
        contact = ContactFactory()
        assert contact.first_name is not None
        assert contact.org is not None
    
    def test_contact_string_representation(self):
        """Test contact string representation."""
        contact = ContactFactory(first_name='John', last_name='Doe')
        assert 'John' in str(contact)
        assert 'Doe' in str(contact)


@pytest.mark.django_db
@pytest.mark.unit
class TestLeadModel:
    """Test Lead model."""
    
    def test_lead_creation(self):
        """Test basic lead creation."""
        lead = LeadFactory()
        assert lead.org is not None
        assert lead.stage in ['new', 'contacted', 'proposal', 'negotiation', 'won', 'lost']
    
    def test_lead_stage_choices(self):
        """Test lead stage choices."""
        lead = LeadFactory(stage='new')
        assert lead.stage == 'new'
        
        lead.stage = 'won'
        lead.save()
        assert lead.stage == 'won'


@pytest.mark.django_db
@pytest.mark.unit
class TestClientModel:
    """Test Client model."""
    
    def test_client_creation(self):
        """Test basic client creation."""
        client = ClientFactory()
        assert client.org is not None
        assert client.status in ['active', 'inactive', 'prospect']













































