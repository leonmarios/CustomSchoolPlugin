from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, JSONWidget
from .models import Learner, FamilyMember

class LearnerResource(resources.ModelResource):
    dynamic_fields = fields.Field(
        column_name='dynamic_fields',
        attribute='dynamic_fields',
        widget=JSONWidget()
    )

    class Meta:
        model = Learner
        import_id_fields = ('folder_name',)
        export_order = ('id', 'first_name', 'last_name', 'folder_name', 
                       'is_active', 'dynamic_fields', 'created_at', 'updated_at')
        fields = export_order
        skip_unchanged = True
        report_skipped = True

    def before_import_row(self, row, **kwargs):
        """Clean and validate data before import"""
        # Convert boolean strings to actual booleans
        if 'is_active' in row:
            row['is_active'] = str(row['is_active']).lower() in ('true', '1', 'yes')
        
        # Ensure folder_name is unique
        folder_name = row.get('folder_name')
        if folder_name:
            existing = Learner.objects.filter(folder_name=folder_name)
            if existing.exists():
                row['folder_name'] = f"{folder_name}_imported_{existing.count()}"

class FamilyMemberResource(resources.ModelResource):
    learner = fields.Field(
        column_name='learner',
        attribute='learner',
        widget=ForeignKeyWidget(Learner, 'folder_name')
    )

    class Meta:
        model = FamilyMember
        import_id_fields = ('learner', 'first_name', 'last_name')
        fields = ('id', 'learner', 'first_name', 'last_name', 'relationship', 
                 'birth_date', 'education', 'occupation', 'health_status', 'order') 