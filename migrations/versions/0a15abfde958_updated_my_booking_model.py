"""updated my booking model

Revision ID: 0a15abfde958
Revises: da5bce15b329
Create Date: 2025-07-05 23:03:48.060142

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0a15abfde958'
down_revision = 'da5bce15b329'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.add_column(sa.Column('full_name', sa.String(length=128), nullable=False))
        batch_op.add_column(sa.Column('phone', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('email', sa.String(length=128), nullable=False))
        batch_op.add_column(sa.Column('id_number', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('driving_license', sa.String(length=50), nullable=False))
        batch_op.add_column(sa.Column('pickup_option', sa.String(length=20), nullable=False))
        batch_op.add_column(sa.Column('delivery_address', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('need_driver', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('special_requests', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('payment_method', sa.String(length=50), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('booking', schema=None) as batch_op:
        batch_op.drop_column('payment_method')
        batch_op.drop_column('special_requests')
        batch_op.drop_column('need_driver')
        batch_op.drop_column('delivery_address')
        batch_op.drop_column('pickup_option')
        batch_op.drop_column('driving_license')
        batch_op.drop_column('id_number')
        batch_op.drop_column('email')
        batch_op.drop_column('phone')
        batch_op.drop_column('full_name')

    # ### end Alembic commands ###
