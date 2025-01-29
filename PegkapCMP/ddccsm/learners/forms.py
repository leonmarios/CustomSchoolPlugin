from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import validate_email
import re
from .models import Learner, FormField, FamilyMember, LearnerFile, Evaluation, SocialHistory
from import_export.formats import base_formats
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .validators import (
    validate_amka, validate_afm, validate_phone, 
    validate_postal_code, clean_text
)
from classes.models import Class
import uuid
from datetime import date

class LearnerForm(forms.ModelForm):
    # Explicitly declare phone fields as optional
    phone = forms.CharField(
        label=_('Τηλέφωνο Ωφελούμενου'),
        max_length=20,
        required=False
    )
    
    emergency_phone = forms.CharField(
        label=_('Τηλέφωνο Δικαστικού Συμπαραστάτη - Έκτακτης Ανάγκης'),
        max_length=20,
        required=False
    )

    amka = forms.CharField(
        label=_('ΑΜΚΑ Ωφελούμενου'),
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'pattern': '[0-9]{11}'  # Keep the validation without the note
        })
    )

    status = forms.ChoiceField(
        label=_('Κατάσταση'),
        choices=[
            ('', _('Επιλέξτε')),
            ('active', _('Ενεργός')),
            ('inactive', _('Ανενεργός')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class_assignment = forms.ModelChoiceField(
        queryset=Class.objects.filter(is_active=True),  # Changed from status='active' to is_active=True
        label=_('Τμήμα'),
        required=False,
        empty_label=_('Επιλέξτε'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Define yes/no choices
    BOOLEAN_CHOICES = [
        ('', _('Επιλογή')),
        (True, _('Ναι')),
        (False, _('Όχι'))
    ]

    heredity_exists = forms.ChoiceField(
        choices=BOOLEAN_CHOICES,
        widget=forms.RadioSelect,
        required=False
    )

    MARITAL_STATUS_CHOICES = [
        ('', _('Επιλέξτε')),
        ('single', _('Άγαμος/η')),
        ('married', _('Έγγαμος/η')),
        ('divorced', _('Διαζευγμένος/η')),
        ('widowed', _('Χήρος/α'))
    ]

    guardian_marital_status = forms.ChoiceField(
        label=_('Οικογενειακή Κατάσταση Δικαστικού Συμπαραστάτη'),
        choices=MARITAL_STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    # Add base guardian email field
    guardian_email = forms.EmailField(
        label=_('Email δικαστικού συμπαραστάτη'),
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control guardian-email',
            'maxlength': '320'
        })
    )

    # Add base sibling field
    sibling_name = forms.CharField(
        label=_('Όνομα Αδερφού/ης'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control sibling-name',
            'data-sibling-index': '0'
        })
    )

    # Add a read-only age field
    calculated_age = forms.CharField(
        label=_('Ηλικία'),
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control form-control-plaintext',
            'tabindex': '-1',
            'aria-readonly': 'true',
        })
    )

    # Add folder name field
    folder_name = forms.CharField(
        label=_('Φάκελος'),
        required=False,
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control form-control-plaintext',
            'tabindex': '-1',
            'aria-readonly': 'true',
        })
    )

    # Update gender field with default empty option
    gender = forms.ChoiceField(
        label=_('Φύλο'),
        choices=[
            ('', _('Επιλέξτε')),  # Added default empty option
            ('male', _('Άνδρας')),
            ('female', _('Γυναίκα'))
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Add a placeholder field for photo spacing
    photo_placeholder = forms.CharField(
        label='',
        required=False,
        widget=forms.HiddenInput()
    )

    # Add placeholders for spacing
    sibling_placeholder = forms.CharField(
        label='',
        required=False,
        widget=forms.HiddenInput()
    )

    # Add birth place field
    birth_place = forms.CharField(
        label=_('Τόπος Γέννησης'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # Update required fields with simpler Greek error messages
    first_name = forms.CharField(
        label=_('Όνομα'),
        error_messages={
            'required': _('Το πεδίο είναι υποχρεωτικό.')
        }
    )
    
    last_name = forms.CharField(
        label=_('Επώνυμο'),
        error_messages={
            'required': _('Το πεδίο είναι υποχρεωτικό.')
        }
    )

    # Update insurance type field with new default option
    insurance_type = forms.ChoiceField(
        label=_('Τρόπος Ασφάλισης'),
        choices=[
            ('', _('Επιλέξτε')),  # Updated default option
            ('direct', _('Άμεσα')),
            ('indirect', _('Έμμεσα')),
            ('welfare', _('Πρόνοια')),
            ('uninsured', _('Ανασφάλιστος')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Update KESY and KEPA fields to be yes/no
    kesy = forms.ChoiceField(
        label=_('ΚΕΣΥ'),
        choices=[
            ('', _('Επιλέξτε')),  # Added empty option
            ('yes', _('Ναι')),
            ('no', _('Όχι'))
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    kepa = forms.ChoiceField(
        label=_('ΚΕΠΑ'),
        choices=[
            ('', _('Επιλέξτε')),  # Added empty option
            ('yes', _('Ναι')),
            ('no', _('Όχι'))
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    arrival_date = forms.DateField(
        label=_('Ημερομηνία Προσέλευσης'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control datepicker',
                'data-date-format': 'dd/mm/yyyy'
            }
        ),
        input_formats=['%d/%m/%Y']
    )

    departure_date = forms.DateField(
        label=_('Ημερομηνία Αποχώρησης'),
        required=False,
        widget=forms.DateInput(
            attrs={
                'class': 'form-control datepicker',
                'data-date-format': 'dd/mm/yyyy'
            }
        ),
        input_formats=['%d/%m/%Y']
    )

    # Development and Health fields
    heredity_details = forms.CharField(
        label=_('Λεπτομέρειες Γενετικού Φαινομένου'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    motor_development = forms.CharField(
        label=_('Κινητική Ανάπτυξη(Βάδισε ελεύθερα)'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    speech_first_words = forms.CharField(
        label=_('Ομιλία - Πρώτες λέξεις'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    speech_sentences = forms.CharField(
        label=_('Ομιλία - Σχηματισμός προτάσεων'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    communication = forms.CharField(
        label=_('Επικοινωνία (με ομιλία, με την χρήση τεχνολογίας/άλλο:)'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    sphincter_control = forms.CharField(
        label=_('Έλεγχος σφιγκτήρων - Εγκόπριση-ενούρηση'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    menstruation = forms.CharField(
        label=_('Έμμηνος ρήση'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    allergies = forms.CharField(
        label=_('Αλλεργίες'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    sexual_education = forms.CharField(
        label=_('Σεξουαλική Διαπαιδαγώγηση'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    epilepsy = forms.CharField(
        label=_('Κρίσεις Επιληψίας'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    other_health_issues = forms.CharField(
        label=_('Άλλα προβλήματα (όραση, ακοή, λόγος, κινητικές δυσκολίες, κλπ)'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    medications = forms.CharField(
        label=_('Φαρμακευτική αγωγή'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    doctor = forms.CharField(
        label=_('Γιατρός'),
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    social_behavior = forms.CharField(
        label=_('Συμπεριφορά/σχέσεις με τους άλλους'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    relationships = forms.CharField(
        label=_('Συντροφικές/Σεξουαλικές Σχέσεις'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    free_time_programs = forms.CharField(
        label=_('Ελεύθερος χρόνος (προγράμματα που παρακολουθεί)'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    free_time_home = forms.CharField(
        label=_('Ελεύθερος χρόνος (ενδιαφέροντα στο σπίτι/χαλάρωση)'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    beneficiary_expectations = forms.CharField(
        label=_('Προσδοκίες ωφελούμενου από τη συμμετοχή στα προγράμματα του Κέντρου'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    parent_expectations = forms.CharField(
        label=_('Προσδοκίες γονέων από τη συμμετοχή στα προγράμματα του Κέντρου'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    welfare_disability = forms.ChoiceField(
        label=_('Επίδομα αναπηρίας'),
        choices=[
            ('', _('Επιλέξτε')),  # Added default option
            ('yes', _('Ναι')),
            ('no', _('Όχι')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    parent_pension = forms.ChoiceField(
        label=_('Σύνταξη γονέα'),
        choices=[
            ('', _('Επιλέξτε')),  # Added default option
            ('yes', _('Ναι')),
            ('no', _('Όχι')),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    # Add this field
    guardian_name = forms.CharField(
        label=_('Όνομα Δικαστικού Συμπαραστάτη'),
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Learner
        exclude = [
            'family_member1_name', 'family_member1_lastname', 'family_member1_relation',
            'family_member1_birthdate', 'family_member1_education', 'family_member1_occupation',
            # ... (exclude fields for members 2-5)
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Update field labels for psychomotor health
        self.fields['motor_development'].label = _('Κινητική Ανάπτυξη(Βάδισε ελεύθερα)')
        self.fields['speech_first_words'].label = _('Ομιλία - Πρώτες λέξεις')
        self.fields['speech_sentences'].label = _('Ομιλία - Σχηματισμός προτάσεων')
        self.fields['communication'].label = _('Επικοινωνία (με ομιλία, με την χρήση τεχνολογίας/άλλο:)')
        self.fields['sphincter_control'].label = _('Έλεγχος σφιγκτήρων - Εγκόπριση-ενούρηση')
        self.fields['menstruation'].label = _('Έμμηνος ρήση')
        self.fields['allergies'].label = _('Αλλεργίες')
        self.fields['sexual_education'].label = _('Σεξουαλική Διαπαιδαγώγηση')
        self.fields['epilepsy'].label = _('Κρίσεις Επιληψίας')
        self.fields['other_health_issues'].label = _('Άλλα προβλήματα (όραση, ακοή, λόγος, κινητικές δυσκολίες, κλπ)')
        self.fields['medications'].label = _('Φαρμακευτική αγωγή')
        self.fields['doctor'].label = _('Γιατρός')

        # Update field labels for other info
        self.fields['kepa_decision'].label = _('Απόφαση ΚΕΠΑ')
        self.fields['kepa_decision_expiry'].label = _('Λήξη απόφασης ΚΕΠΑ')
        self.fields['eopyy_opinions'].label = _('Ιατρικές Γνωματεύσεις ΕΟΠΥΥ')
        self.fields['eopyy_opinions_expiry'].label = _('Λήξη Γνωματεύσεων ΕΟΠΥΥ')
        self.fields['insurance_capacity'].label = _('Ασφαλιστική ικανότητα')
        self.fields['insurance_capacity_expiry'].label = _('Λήξη Ασφαλιστικής ικανότητας')
        self.fields['unemployment_card'].label = _('Κάρτα Ανεργίας')
        self.fields['kdhf'].label = _('ΚΔΗΦ')
        self.fields['bus_route_escort'].label = _('Πούλμαν/Δρομολόγιο/Συνοδός')

        self.field_groups = {
            'personal_info': [
                'photo', 'photo_placeholder',
                'first_name', 'last_name',
                'father_first_name', 'father_last_name',
                'mother_first_name', 'mother_last_name',
                'sibling_name', 'sibling_placeholder',
                'guardian_first_name', 'guardian_last_name',
                'birth_date', 'calculated_age',
                'gender', 'birth_place',
                'marital_status', 'guardian_marital_status',
                'phone', 'email',
                'emergency_phone', 'guardian_email',
                'address', 'placeholder',
                'id_number', 'amka',
                'insurance_type', 'insurance_fund',
                'ama', 'guardian_ama',
                'tax_number', 'judicial_support',
                'court_decision', 'inclusion_agreement',
                'gdpr', 'referral',
                'other_info'
            ],
            'family_info': [
                # Remove old family member fields from this group
            ],
            'social_history': [
                'status', 
                'arrival_date', 
                'rv_team',
                'decision_announcement',
                'class_assignment',
                'departure_date'
            ],
            'expert_opinions': [
                'kesy', 
                'kepa',
                'other_opinions'
            ],
            'psychomotor_health': [
                'motor_development',
                'speech_first_words',
                'speech_sentences',
                'communication',
                'sphincter_control',
                'menstruation',
                'allergies',
                'sexual_education',
                'epilepsy',
                'other_health_issues',
                'medications',
                'doctor'
            ],
            'education': [
                'preschool',
                'elementary',
                'middle_school',
                'high_school',
                'special_school',
                'special_workshop',
                'other_education'
            ],
            'school_achievements': [
                'reading',
                'writing',
                'arithmetic',
                'money_management',
                'time_management'
            ],
            'skills_behavior': [
                'dressing',
                'eating',
                'personal_hygiene',
                'toilet',
                'house_chores',
                'mobility_shopping',
                'social_behavior',
                'relationships',
                'free_time_programs',
                'free_time_home',
                'beneficiary_expectations',
                'parent_expectations',
                'other_skills_info'
            ],
            'other_info': [
                'kepa_decision',                  # 1. Απόφαση ΚΕΠΑ
                'kepa_decision_expiry',           # 2. Λήξη απόφασης ΚΕΠΑ
                'eopyy_opinions',                 # 3. Ιατρικές Γνωματεύσεις ΕΟΠΥΥ
                'eopyy_opinions_expiry',          # 4. Λήξη Γνωματεύσεων ΕΟΠΥΥ
                'insurance_capacity',             # 5. Ασφαλιστική ικανότητα
                'insurance_capacity_expiry',      # 6. Λήξη Ασφαλιστικής ικανότητας
                'unemployment_card',              # 7. Κάρτα Ανεργίας
                'kdhf',                          # 8. ΚΔΗΦ
                'bus_route_escort'                # 9. Πούλμαν/Δρομολόγιο/Συνοδός
            ],
            'benefits_pension': [
                'welfare_disability',
                'welfare_disability_other',
                'parent_pension'
            ],
            'comments': [
                'comments'
            ]
        }

        # Add choices for marital status fields
        MARITAL_STATUS_CHOICES = [
            ('', _('Επιλέξτε')),
            ('single', _('Άγαμος/η')),
            ('married', _('Έγγαμος/η')),
            ('divorced', _('Διαζευγμένος/η')),
            ('widowed', _('Χήρος/α'))
        ]

        # Add the fields with their choices
        self.fields['marital_status'] = forms.ChoiceField(
            label=_('Οικογενειακή Κατάσταση'),
            choices=MARITAL_STATUS_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        self.fields['guardian_marital_status'] = forms.ChoiceField(
            label=_('Οικογενειακή Κατάσταση Δικαστικού Συμπαραστάτη'),
            choices=MARITAL_STATUS_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-control'})
        )

        # Calculate initial age if birth_date exists
        if self.instance.birth_date:
            self.initial['calculated_age'] = self.calculate_age(self.instance.birth_date)

        # Make all fields optional except first_name and last_name
        required_fields = ['first_name', 'last_name']
        for field_name, field in self.fields.items():
            if field_name not in required_fields:
                field.required = False
        
        # Ensure AMKA is not required
        self.fields['amka'].required = False
        
        # Add date picker widget for all date fields
        date_fields = [
            'birth_date', 'arrival_date', 'departure_date',
            'eopyy_opinions_expiry', 'kepa_decision_expiry', 'insurance_capacity_expiry'
        ]
        
        for field_name in date_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = forms.DateInput(
                    attrs={'type': 'date', 'class': 'form-control'}
                )
        
        # Add Bootstrap classes to all fields
        for field in self.fields.values():
            if isinstance(field.widget, (forms.TextInput, forms.Select, forms.NumberInput, forms.DateInput)):
                field.widget.attrs.update({'class': 'form-control'})

        # Generate a unique identifier
        self.unique_id = str(uuid.uuid4())[:8]
        
        # Initialize guardian emails
        if self.instance.pk and self.instance.additional_guardian_emails:
            # First email goes to the main guardian_email field
            if len(self.instance.additional_guardian_emails) > 0:
                self.initial['guardian_email'] = self.instance.additional_guardian_emails[0]
            
            # Add additional email fields for any remaining emails
            for i, email in enumerate(self.instance.additional_guardian_emails[1:], start=1):
                field_name = f'guardian_email_{i}'
                self.fields[field_name] = forms.EmailField(
                    label=_('Επιπλέον Email Δικαστικού Συμπαραστάτη'),
                    required=False,
                    widget=forms.EmailInput(attrs={
                        'class': 'form-control guardian-email',
                        'data-email-index': str(i)
                    })
                )
                self.initial[field_name] = email

        # Initialize sibling names
        if self.instance.pk:
            sibling_names = []
            if self.instance.sibling_name_1:
                sibling_names.append(self.instance.sibling_name_1)
            if self.instance.sibling_name_2:
                sibling_names.append(self.instance.sibling_name_2)
            if self.instance.sibling_name_3:
                sibling_names.append(self.instance.sibling_name_3)
            
            # Set initial values
            for i, name in enumerate(sibling_names):
                if i == 0:
                    self.initial['sibling_name'] = name
                else:
                    self.fields[f'sibling_name_{i+1}'] = forms.CharField(
                        required=False,
                        widget=forms.TextInput(attrs={
                            'class': 'form-control sibling-name',
                            'data-sibling-index': str(i)
                        })
                    )
                    self.initial[f'sibling_name_{i+1}'] = name

        # Explicitly remove the age field if it exists
        if 'age' in self.fields:
            del self.fields['age']
        
        # Update demographics group to remove age and ensure calculated_age is in the right place
        if 'personal_info' in self.field_groups:
            # Remove old age field if present
            self.field_groups['personal_info'] = [
                field for field in self.field_groups['personal_info'] 
                if field != 'age'
            ]
            
            # Ensure calculated_age is in the right position
            if 'birth_date' in self.field_groups['personal_info']:
                birth_date_index = self.field_groups['personal_info'].index('birth_date')
                # Remove calculated_age if it exists (to avoid duplicates)
                if 'calculated_age' in self.field_groups['personal_info']:
                    self.field_groups['personal_info'].remove('calculated_age')
                # Insert calculated_age after birth_date
                self.field_groups['personal_info'].insert(birth_date_index + 1, 'calculated_age')

        # Calculate initial folder name if instance exists
        if self.instance.pk and self.instance.first_name and self.instance.last_name:
            self.initial['folder_name'] = f"{self.instance.first_name} {self.instance.last_name}"

        # Update all date fields to use dd/mm/yyyy format
        date_fields = [
            'birth_date',
            'member1_birth_date',
            'member2_birth_date',
            'member3_birth_date',
            'member4_birth_date',
            'member5_birth_date'
        ]

        for field_name in date_fields:
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.update({
                    'class': 'form-control datepicker',
                    'data-date-format': 'dd/mm/yyyy'
                })
                self.fields[field_name].input_formats = ['%d/%m/%Y']

    @staticmethod
    def calculate_age(birth_date):
        today = date.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return f"{age} ετών"

    def clean(self):
        cleaned_data = super().clean()
        
        # Clean text fields
        text_fields = ['first_name', 'last_name', 'address', 'city']
        for field in text_fields:
            if field in cleaned_data:
                cleaned_data[field] = clean_text(cleaned_data[field])
        
        # Collect all guardian emails from the form
        guardian_emails = []
        for key in self.data.keys():
            if key.startswith('guardian_email_') and self.data[key]:
                guardian_emails.append(self.data[key])
        cleaned_data['additional_guardian_emails'] = guardian_emails
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Save dynamic fields to the JSON field
        dynamic_fields = {}
        for field_name, field in self.fields.items():
            if hasattr(field, 'field_object'):
                value = self.cleaned_data.get(field_name)
                if value is not None:
                    dynamic_fields[field_name] = value
        
        instance.dynamic_fields = dynamic_fields
        
        # Save all guardian emails to the JSONField
        instance.additional_guardian_emails = self.cleaned_data.get('additional_guardian_emails', [])
        # Clear the old fixed email fields
        instance.guardian_email = None
        instance.guardian_email_2 = None
        
        # Update the sibling name fields
        instance.sibling_name_1 = self.cleaned_data.get('sibling_name_1', '')
        instance.sibling_name_2 = self.cleaned_data.get('sibling_name_2', '')
        instance.sibling_name_3 = self.cleaned_data.get('sibling_name_3', '')
        
        if commit:
            instance.save()
        
        return instance

    def parse_family_member_data(self, data):
        try:
            return {
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'relationship': data.get('relationship', ''),
                'birth_date': data.get('birth_date'),
                'education': data.get('education', ''),
                'occupation': data.get('occupation', ''),
                'health_status': data.get('health_status', ''),
                'order': data.get('order', 0)
            }
        except (KeyError, ValueError):
            return None

    def clean_folder_name(self):
        folder_name = self.cleaned_data.get('folder_name')
        if folder_name:
            # Check if folder name is unique
            qs = Learner.objects.filter(folder_name=folder_name)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise ValidationError(_('Αυτό το όνομα φακέλου χρησιμοποιείται ήδη.'))
        return folder_name

    def clean_amka(self):
        amka = self.cleaned_data.get('amka')
        if not amka:
            return ''
        if len(amka) != 11:
            raise forms.ValidationError(_('Ο ΑΜΚΑ πρέπει να αποτελείται από 11 ψηφία.'))
        if not amka.isdigit():
            raise forms.ValidationError(_('Ο ΑΜΚΑ πρέπει να περιέχει μόνο ψηφία.'))
        return amka

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone:  # If empty or None, return empty string
            return ''
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone))
        if phone and len(phone) < 10:
            raise forms.ValidationError(_('Μη έγκυρος αριθμός τηλεφώνου.'))
        return phone

    def clean_emergency_phone(self):
        phone = self.cleaned_data.get('emergency_phone')
        if not phone:  # If empty or None, return empty string
            return ''
        # Remove any spaces or special characters
        phone = ''.join(filter(str.isdigit, phone))
        if phone and len(phone) < 10:
            raise forms.ValidationError(_('Μη έγκυρος αριθμός τηλεφώνου.'))
        return phone

class ImportForm(forms.Form):
    import_file = forms.FileField(
        label=_('Αρχείο Εισαγωγής'),
        help_text=_('Υποστηριζόμενοι τύποι: .xlsx, .csv')
    )
    import_format = forms.ChoiceField(
        label=_('Μορφή Αρχείου'),
        choices=[
            (base_formats.XLSX, 'Excel (.xlsx)'),
            (base_formats.CSV, 'CSV'),
        ]
    )

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'groups')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            # Don't require password for existing users
            self.fields.pop('password1')
            self.fields.pop('password2')
        
        self.fields['groups'].widget = forms.CheckboxSelectMultiple()
        self.fields['groups'].queryset = Group.objects.all()

class EvaluationForm(forms.ModelForm):
    evaluation_date = forms.DateField(
        label=_('Ημερομηνία Αξιολόγησης'),
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Evaluation
        fields = ['evaluation_type', 'evaluation_date', 'comments']
        labels = {
            'evaluation_type': _('Τύπος Αξιολόγησης'),
            'comments': _('Σχόλια Αξιολόγησης'),
        }
        widgets = {
            'evaluation_type': forms.Select(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['evaluation_type'].widget.attrs.update({'class': 'form-control'})

class LearnerSelectForm(forms.Form):
    learner = forms.ModelChoiceField(
        queryset=Learner.objects.filter(status='active'),
        label=_('Ωφελούμενος'),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class FamilyMemberForm(forms.Form):
    family_member_first_name = forms.CharField(
        label=_('Όνομα'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )
    
    family_member_last_name = forms.CharField(
        label=_('Επώνυμο'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )
    
    family_member_relation = forms.CharField(
        label=_('Συγγενική σχέση'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )
    
    family_member_birth_date = forms.DateField(
        label=_('Ημερομηνία γέννησης'),
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control family-member-field datepicker',
            'data-member-index': '0'
        })
    )
    
    family_member_education = forms.CharField(
        label=_('Εκπαίδευση'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )
    
    family_member_occupation = forms.CharField(
        label=_('Επάγγελμα'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )
    
    family_member_health = forms.CharField(
        label=_('Κατάσταση υγείας'),
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control family-member-field',
            'data-member-index': '0'
        })
    )

class SocialHistoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = SocialHistory
        fields = ['status', 'arrival_date', 'rv_team', 'interdisciplinary_team', 'comments']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        # Get all emails from the form
        emails = self.data.getlist('guardian_emails[]')
        # Filter out empty values and store as JSON
        cleaned_data['guardian_emails'] = [email.strip() for email in emails if email.strip()]
        return cleaned_data 