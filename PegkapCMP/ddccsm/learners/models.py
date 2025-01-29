from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.serializers.json import DjangoJSONEncoder
import os
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from classes.models import Class  # Import the Class model
from django.conf import settings
from django.utils import timezone
from datetime import date

def validate_amka(value):
    if value and not value.isdigit():
        raise ValidationError(_('Ο ΑΜΚΑ πρέπει να περιέχει μόνο ψηφία.'))
    if value and len(value) != 11:
        raise ValidationError(_('Ο ΑΜΚΑ πρέπει να αποτελείται από 11 ψηφία.'))

class SocialHistory(models.Model):
    STATUS_CHOICES = [
        ('active', _('Ενεργός')),
        ('inactive', _('Ανενεργός')),
        ('pending', _('Σε αναμονή')),
    ]

    learner = models.OneToOneField(
        'Learner',
        on_delete=models.CASCADE,
        related_name='social_history',
        verbose_name=_('Ωφελούμενος')
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name=_('Κατάσταση')
    )
    
    arrival_date = models.DateField(
        verbose_name=_('Ημερομηνία Προσέλευσης'),
        default=timezone.now,
        null=True,
        blank=True
    )
    
    rv_team = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('RV Διεπιστημονική Ομάδα')
    )
    
    interdisciplinary_team = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Διεπιστημονική Ομάδα')
    )
    
    comments = models.TextField(
        blank=True,
        verbose_name=_('Σχόλια')
    )

    created_at = models.DateTimeField(
        verbose_name=_('Ημερομηνία Δημιουργίας'),
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        verbose_name=_('Τελευταία Ενημέρωση'),
        default=timezone.now
    )

    class Meta:
        verbose_name = _('Κοινωνικό Ιστορικό')
        verbose_name_plural = _('Κοινωνικά Ιστορικά')

    def save(self, *args, **kwargs):
        if not self.pk:  # If this is a new instance
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Social History for {self.learner}"

class FamilyMember(models.Model):
    learner = models.ForeignKey('Learner', on_delete=models.CASCADE, related_name='family_members')
    first_name = models.CharField(_('Όνομα'), max_length=100)
    last_name = models.CharField(_('Επώνυμο'), max_length=100)
    relation = models.CharField(_('Συγγενική σχέση'), max_length=100)
    birth_date = models.DateField(_('Ημερομηνία γέννησης'), null=True, blank=True)
    education = models.CharField(_('Εκπαίδευση'), max_length=100, blank=True)
    occupation = models.CharField(_('Επάγγελμα'), max_length=100, blank=True)
    health_status = models.CharField(_('Κατάσταση υγείας'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('Μέλος Οικογένειας')
        verbose_name_plural = _('Μέλη Οικογένειας')

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.relation})"

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', _('Κείμενο')),
        ('textarea', _('Πολλαπλό Κείμενο')),
        ('number', _('Αριθμός')),
        ('date', _('Ημερομηνία')),
        ('email', _('Email')),
        ('phone', _('Τηλέφωνο')),
        ('file', _('Αρχείο')),
        ('radio', _('Radio Buttons')),
        ('select', _('Dropdown')),
        ('checkbox', _('Checkbox')),
    ]

    name = models.CharField(_('Όνομα Πεδίου'), max_length=100, unique=True)
    label = models.CharField(_('Ετικέτα'), max_length=200)
    field_type = models.CharField(_('Τύπος Πεδίου'), max_length=20, choices=FIELD_TYPES)
    required = models.BooleanField(_('Υποχρεωτικό'), default=False)
    help_text = models.CharField(_('Βοηθητικό Κείμενο'), max_length=200, blank=True)
    choices = models.TextField(_('Επιλογές'), blank=True, help_text=_('Μία επιλογή ανά γραμμή (για radio/select)'))
    section = models.CharField(_('Ενότητα'), max_length=100, default='general')
    order = models.PositiveIntegerField(_('Σειρά'), default=0)
    is_active = models.BooleanField(_('Ενεργό'), default=True)

    class Meta:
        ordering = ['section', 'order']
        verbose_name = _('Πεδίο Φόρμας')
        verbose_name_plural = _('Πεδία Φόρμας')

    def __str__(self):
        return f"{self.label} ({self.field_type})"

    def get_choices_list(self):
        if not self.choices:
            return []
        return [choice.strip() for choice in self.choices.split('\n') if choice.strip()]

class LearnerFile(models.Model):
    learner = models.ForeignKey('Learner', on_delete=models.CASCADE, related_name='files')
    field_name = models.CharField(max_length=100)
    file = models.FileField(upload_to='learner_files/')
    filename = models.CharField(max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Αρχείο Ωφελούμενου')
        verbose_name_plural = _('Αρχεία Ωφελούμενων')
        
    def __str__(self):
        return f"File for {self.learner}: {self.filename}"

class Learner(models.Model):
    STATUS_CHOICES = [
        ('active', _('Ενεργός')),
        ('inactive', _('Ανενεργός')),
    ]

    # Choices
    MARITAL_STATUS_CHOICES = [
        ('single', 'Άγαμος'),
        ('married', 'Έγγαμος'),
        ('divorced', 'Διαζευγμένος'),
    ]

    INSURANCE_TYPE_CHOICES = [
        ('direct', 'Άμεσα Ασφαλισμένος'),
        ('indirect', 'Έμμεσα Ασφαλισμένος'),
    ]

    YES_NO_CHOICES = [
        ('yes', 'Ναι'),
        ('no', 'Όχι'),
    ]

    DISABILITY_CHOICES = [
        ('no', 'Όχι'),
        ('67', '67%'),
        ('80', '80%'),
        ('other', 'Άλλο'),
    ]

    GENDER_CHOICES = [
        ('male', _('Άνδρας')),
        ('female', _('Γυναίκα'))
    ]

    # Add these choices
    DISABILITY_PERCENTAGE_CHOICES = [
        ('67', '67%'),
        ('80', '80%'),
        ('other', _('Άλλο')),
    ]

    # Only these fields are mandatory
    first_name = models.CharField(max_length=100, verbose_name=_('Όνομα'))
    last_name = models.CharField(max_length=100, verbose_name=_('Επώνυμο'))
    birth_date = models.DateField(
        verbose_name=_('Ημερομηνία Γέννησης'),
        null=True,  # Allow null temporarily
        blank=True  # Allow blank temporarily
    )
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='male',
        verbose_name=_('Φύλο')
    )
    
    # Add status field with default as active
    status = models.CharField(
        _('Κατάσταση'),
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    
    # Phone fields with optional validation
    phone = models.CharField(
        _('Τηλέφωνο Ωφελούμενου'), 
        max_length=20, 
        blank=True, 
        null=True
    )
    emergency_phone = models.CharField(
        _('Τηλ. Δ.Σ./ Έκτακτης Ανάγκης'), 
        max_length=20, 
        blank=True, 
        null=True
    )
    
    # AMKA with custom validation
    amka = models.CharField(
        _('ΑΜΚΑ Ωφελούμενου'), 
        max_length=11, 
        blank=True, 
        null=True,
        validators=[validate_amka]
    )
    
    # All other fields are optional
    arrival_date = models.DateField(_('Ημερομηνία Προσέλευσης'), blank=True, null=True)
    rv_team = models.CharField(_('RV Διεπιστημονική Ομάδα'), max_length=100, blank=True, null=True)
    decision_announcement = models.CharField(_('Ανακοίνωση Απόφασης'), max_length=100, blank=True, null=True)
    class_assignment = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Τμήμα'),
        related_name='learners'
    )
    departure_date = models.DateField(_('Ημερομηνία Αποχώρησης'), blank=True, null=True)
    photo = models.ImageField(_('Φωτογραφία'), upload_to='learner_photos/', blank=True, null=True)
    father_first_name = models.CharField(_('Όνομα Πατρός'), max_length=100, blank=True, null=True)
    father_last_name = models.CharField(_('Επώνυμο Πατρός'), max_length=100, blank=True, null=True)
    mother_first_name = models.CharField(_('Όνομα Μητρός'), max_length=100, blank=True, null=True)
    mother_last_name = models.CharField(_('Επώνυμο Μητρός'), max_length=100, blank=True, null=True)
    sibling_name_1 = models.CharField(_('Όνομα Αδερφού/ης 1'), max_length=100, blank=True, null=True)
    sibling_name_2 = models.CharField(_('Όνομα Αδερφού/ης 2'), max_length=100, blank=True, null=True)
    sibling_name_3 = models.CharField(_('Όνομα Αδερφού/ης 3'), max_length=100, blank=True, null=True)
    guardian_first_name = models.CharField(_('Όνομα Δικαστικού Συμπαραστάτη'), max_length=100, blank=True, null=True)
    guardian_last_name = models.CharField(_('Επώνυμο Δικαστικού Συμπαραστάτη'), max_length=100, blank=True, null=True)
    age = models.IntegerField(_('Ηλικία'), blank=True, null=True)
    birth_place = models.CharField(_('Τόπος Γέννησης'), max_length=100, blank=True, null=True)
    marital_status = models.CharField(
        _('Οικογενειακή Κατάσταση'),
        max_length=20,
        blank=True,
        null=True
    )
    guardian_marital_status = models.CharField(
        _('Οικογενειακή Κατάσταση Δικαστικού Συμπαραστάτη'),
        max_length=20,
        blank=True,
        null=True
    )
    address = models.CharField(_('Διεύθυνση'), max_length=200, blank=True, null=True)
    email = models.EmailField(_('Email ωφελούμενου'), blank=True, null=True)
    guardian_email = models.EmailField(_('Email δικαστικού συμπαραστάτη'), blank=True, null=True)
    guardian_email_2 = models.EmailField(_('Email δικαστικού συμπαραστάτη 2'), blank=True, null=True)
    id_number = models.CharField(_('Α.Δ.Τ. ωφελούμενου'), max_length=20, blank=True, null=True)
    insurance_type = models.CharField(_('Τρόπος ασφάλισης'), 
                                    max_length=20, 
                                    choices=INSURANCE_TYPE_CHOICES,
                                    blank=True, null=True)
    insurance_fund = models.CharField(_('Ασφαλιστικό Ταμείο'), max_length=100, blank=True, null=True)
    ama = models.CharField(_('ΑΜΑ Ωφελούμενου'), max_length=20, blank=True, null=True)
    guardian_ama = models.CharField(_('ΑΜΑ Αμεσα Ασφαλισμένου'), max_length=20, blank=True, null=True)
    tax_number = models.CharField(_('ΑΦΜ'), max_length=9, blank=True, null=True)
    judicial_support = models.CharField(_('Δικαστική Συμπαράσταση'), max_length=200, blank=True, null=True)
    court_decision = models.CharField(_('Απόφαση Δικαστηρίου'), max_length=200, blank=True, null=True)
    inclusion_agreement = models.CharField(_('Συμφωνία Ένταξης'), max_length=200, blank=True, null=True)
    gdpr = models.CharField(_('GDPR'), max_length=200, blank=True, null=True)
    referral = models.CharField(_('Παραπομπή'), max_length=200, blank=True, null=True)
    other_info = models.TextField(_('Άλλη πληροφορία'), blank=True, null=True)
    kesy = models.CharField(_('Κέντρα Εκπαιδευτικής και Συμβουλευτικής Υποστήριξης (ΚΕΣΥ)'),
                           max_length=3,
                           choices=YES_NO_CHOICES,
                           blank=True, null=True)
    kepa = models.CharField(_('Κέντρο Πιστοποίησης Αναπηρίας (ΚΕΠΑ)'),
                           max_length=3,
                           choices=YES_NO_CHOICES,
                           blank=True, null=True)
    other_opinions = models.TextField(_('Άλλες Γνωματεύσεις'), blank=True, null=True)
    heredity_exists = models.CharField(_('Ύπαρξη Κληρονομικότητας'),
                                     max_length=3,
                                     choices=YES_NO_CHOICES,
                                     blank=True, null=True)
    heredity_details = models.TextField(_('Κληρονομικότητα'), blank=True, null=True)
    motor_development = models.CharField(_('Κινητική Ανάπτυξη(Βάδισε ελεύθερα)'), max_length=200, blank=True, null=True)
    speech_first_words = models.CharField(_('Ομιλία - Πρώτες λέξεις'), max_length=200, blank=True, null=True)
    speech_sentences = models.CharField(_('Ομιλία - Σχηματισμός προτάσεων'), max_length=200, blank=True, null=True)
    communication = models.CharField(_('Επικοινωνία (με ομιλία, με την χρήση τεχνολογίας/άλλο:)'), max_length=200, blank=True, null=True)
    sphincter_control = models.CharField(_('Έλεγχος σφιγκτήρων - Εγκόπριση-ενούρηση'), max_length=200, blank=True, null=True)
    menstruation = models.CharField(_('Έμμηνος ρήση'), max_length=200, blank=True, null=True)
    allergies = models.CharField(_('Αλλεργίες'), max_length=200, blank=True, null=True)
    sexual_education = models.CharField(_('Σεξουαλική Διαπαιδαγώγηση'), max_length=200, blank=True, null=True)
    epilepsy = models.CharField(_('Κρίσεις Επιληψίας'), max_length=200, blank=True, null=True)
    other_health_issues = models.TextField(_('Άλλα προβλήματα (όραση, ακοή, λόγος, κινητικές δυσκολίες, κλπ)'), blank=True, null=True)
    medications = models.TextField(_('Φαρμακευτική αγωγή'), blank=True, null=True)
    doctor = models.CharField(_('Γιατρός'), max_length=200, blank=True, null=True)
    preschool = models.CharField(_('Προσχολική Αγωγή'), max_length=200, blank=True, null=True)
    elementary = models.CharField(_('Δημοτικό'), max_length=200, blank=True, null=True)
    middle_school = models.CharField(_('Γυμνάσιο'), max_length=200, blank=True, null=True)
    high_school = models.CharField(_('Λύκειο'), max_length=200, blank=True, null=True)
    special_school = models.CharField(_('Σχολείο Ειδικής Αγωγής'), max_length=200, blank=True, null=True)
    special_workshop = models.CharField(_('Εργαστήριο Ειδικής Αγωγής'), max_length=200, blank=True, null=True)
    other_education = models.TextField(_('Άλλο (π.χ. όπως προγράμματα: εργοθεραπείας/ αισθητηριακής ολοκλήρωσης, λογοθεραπείας/πρώιμης παρέμβασης κ.τ.λ.)'), blank=True, null=True)
    reading = models.CharField(_('Ανάγνωση'), max_length=200, blank=True, null=True)
    writing = models.CharField(_('Γραφή'), max_length=200, blank=True, null=True)
    arithmetic = models.CharField(_('Αριθμητική'), max_length=200, blank=True, null=True)
    money_management = models.CharField(_('Χρήματα'), max_length=200, blank=True, null=True)
    time_management = models.CharField(_('Ώρα'), max_length=200, blank=True, null=True)
    dressing = models.CharField(_('Ντύσιμο-γδύσιμο'), max_length=200, blank=True, null=True)
    eating = models.CharField(_('Φαγητό'), max_length=200, blank=True, null=True)
    personal_hygiene = models.CharField(_('Ατομική καθαριότητα'), max_length=200, blank=True, null=True)
    toilet = models.CharField(_('Τουαλέτα'), max_length=200, blank=True, null=True)
    house_chores = models.CharField(_('Συμμετοχή στις δουλειές του σπιτιού'), max_length=200, blank=True, null=True)
    mobility_shopping = models.CharField(_('Κυκλοφορία – ψώνια – διαχείριση χρημάτων'), max_length=200, blank=True, null=True)
    social_behavior = models.TextField(_('Συμπεριφορά/σχέσεις με τους άλλους'), blank=True, null=True)
    relationships = models.TextField(_('Συντροφικές/Σεξουαλικές Σχέσεις'), blank=True, null=True)
    free_time_programs = models.TextField(_('Ελεύθερος χρόνος (προγράμματα που παρακολουθεί)'), blank=True, null=True)
    free_time_home = models.TextField(_('Ελεύθερος χρόνος (ενδιαφέροντα στο σπίτι/χαλάρωση)'), blank=True, null=True)
    other_skills_info = models.TextField(_('Άλλες πληροφορίες'), blank=True, null=True)
    beneficiary_expectations = models.TextField(_('Προσδοκίες ωφελούμενου από τη συμμετοχή στα προγράμματα του Κέντρου'), blank=True, null=True)
    parent_expectations = models.TextField(_('Προσδοκίες γονέων από τη συμμετοχή στα προγράμματα του Κέντρου'), blank=True, null=True)
    kepa_decision = models.CharField(_('Απόφαση ΚΕΠΑ'), max_length=200, blank=True, null=True)
    eopyy_opinions = models.CharField(_('Ιατρικές Γνωματεύσεις ΕΟΠΥΥ'), max_length=200, blank=True, null=True)
    eopyy_opinions_expiry = models.DateField(_('Λήξη Γνωματεύσεων ΕΟΠΥΥ'), null=True, blank=True)
    kepa_decision_expiry = models.DateField(_('Λήξη απόφασης ΚΕΠΑ'), null=True, blank=True)
    insurance_capacity = models.CharField(_('Ασφαλιστική ικανότητα'), max_length=200, blank=True, null=True)
    insurance_capacity_expiry = models.DateField(_('Λήξη Ασφαλιστικής ικανότητας'), null=True, blank=True)
    unemployment_card = models.CharField(_('Κάρτα Ανεργίας'), max_length=200, blank=True, null=True)
    kdhf = models.CharField(_('ΚΔΗΦ'), max_length=200, blank=True, null=True)
    department = models.CharField(_('TMHMA'), max_length=200, blank=True, null=True)
    bus_route_escort = models.CharField(_('Πούλμαν/Δρομολόγιο/Συνοδός'), max_length=200, blank=True, null=True)
    welfare_disability = models.CharField(_('Προνοιακό επίδομα με ποσοστό αναπηρίας'),
                                        max_length=10,
                                        choices=DISABILITY_CHOICES,
                                        blank=True, null=True)
    welfare_disability_other = models.CharField(_('Άλλο ποσοστό αναπηρίας'), max_length=50, blank=True, null=True)
    parent_pension = models.CharField(_('Σύνταξη ασφαλισμένου συνταξιούχου γονέα (λόγω θανάτου)'),
                                    max_length=3,
                                    choices=YES_NO_CHOICES,
                                    blank=True, null=True)
    comments = models.TextField(_('Σχόλια - Παρατηρήσεις'), blank=True, null=True)
    interdisciplinary_team = models.CharField(_('Διεπιστημονική Ομάδα'), max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    # Add these fields
    disability_percentage = models.CharField(
        max_length=10,
        choices=DISABILITY_PERCENTAGE_CHOICES,
        default='67',
        verbose_name=_('Ποσοστό Αναπηρίας')
    )
    
    other_disability_percentage = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Άλλο ποσοστό αναπηρίας'),
        help_text=_('Συμπληρώστε εάν επιλέξατε "Άλλο"')
    )

    # Additional fields
    additional_guardian_emails = models.JSONField(default=list, blank=True)

    class Meta:
        verbose_name = _('Learner')
        verbose_name_plural = _('Learners')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else "Unnamed Learner"

    def get_file_for_field(self, field_name):
        try:
            return self.files.get(field_name=field_name)
        except LearnerFile.DoesNotExist:
            return None

    def calculate_age(self):
        today = date.today()
        if self.birth_date:
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            return age
        return None

    def get_age_display(self):
        age = self.calculate_age()
        if age is not None:
            return f"{age} ετών"
        return "Μη διαθέσιμο"

@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """Create default user groups and permissions after migration"""
    if sender.name == 'learners':
        # Admin Group
        admin_group, _ = Group.objects.get_or_create(name='Administrators')
        admin_perms = Permission.objects.filter(
            content_type__app_label='learners',
        )
        admin_group.permissions.set(admin_perms)

        # Staff Group (can view and edit, but not delete)
        staff_group, _ = Group.objects.get_or_create(name='Staff')
        staff_perms = Permission.objects.filter(
            content_type__app_label='learners',
            codename__in=['view_learner', 'add_learner', 'change_learner',
                         'view_familymember', 'add_familymember', 'change_familymember']
        )
        staff_group.permissions.set(staff_perms)

        # Viewer Group (read-only access)
        viewer_group, _ = Group.objects.get_or_create(name='Viewers')
        viewer_perms = Permission.objects.filter(
            content_type__app_label='learners',
            codename__in=['view_learner', 'view_familymember']
        )
        viewer_group.permissions.set(viewer_perms)

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('create', _('Δημιουργία')),
        ('update', _('Ενημέρωση')),
        ('delete', _('Διαγραφή')),
        ('import', _('Εισαγωγή')),
        ('export', _('Εξαγωγή')),
        ('login', _('Σύνδεση')),
        ('logout', _('Αποσύνδεση')),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Χρήστης')
    )
    action = models.CharField(
        _('Ενέργεια'),
        max_length=20,
        choices=ACTION_CHOICES
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('Τύπος Περιεχομένου')
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    changes = models.JSONField(_('Αλλαγές'), null=True, blank=True)
    timestamp = models.DateTimeField(_('Χρονική Στιγμή'), auto_now_add=True)
    ip_address = models.GenericIPAddressField(_('Διεύθυνση IP'), null=True)

    class Meta:
        verbose_name = _('Καταγραφή Ενεργειών')
        verbose_name_plural = _('Καταγραφές Ενεργειών')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.timestamp}"

class Evaluation(models.Model):
    EVALUATION_TYPES = [
        ('3month', 'Τρίμηνη'),
        ('6month', 'Εξάμηνη'),
        ('adhoc', 'Έκτακτη'),
    ]

    learner = models.ForeignKey('Learner', on_delete=models.CASCADE, related_name='evaluations')
    evaluation_type = models.CharField(max_length=10, choices=EVALUATION_TYPES)
    evaluation_date = models.DateField()
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-evaluation_date']

    def __str__(self):
        return f"{self.get_evaluation_type_display()} - {self.evaluation_date}"
