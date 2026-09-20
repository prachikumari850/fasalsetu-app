from app.models.claim import Claim, ClaimStatus, DamageType
from app.models.crop import Advisory, AdvisoryPriority, CropStage, CropStageName, DiseaseReport, SeverityLevel
from app.models.user import User, UserRole


def test_sqlalchemy_enum_names_match_the_existing_supabase_schema():
    expected = {
        (CropStage, "stage_name", CropStageName): "crop_stage_name",
        (DiseaseReport, "severity", SeverityLevel): "severity_level",
        (Advisory, "priority", AdvisoryPriority): "advisory_priority",
        (User, "role", UserRole): "user_role",
        (Claim, "status", ClaimStatus): "claim_status",
        (Claim, "damage_type", DamageType): "damage_type",
    }
    for (model, column, _), type_name in expected.items():
        assert model.__table__.c[column].type.name == type_name
