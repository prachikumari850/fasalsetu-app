"""Record the pre-existing Supabase schema as Alembic baseline.

The project was deployed with schema SQL outside Alembic.  This revision is
intentionally non-destructive: it only establishes migration tracking and
does not drop, recreate, or alter production tables or enum values.
"""

revision = "20260920_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
