"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create date: ${create_date}
"""

from typing import Sequence, Union

import sqlalchemy
from alembic import op

${imports if imports else ""}

# Revision identifiers, used by Alembic.
revision: str = ${repr(up_revision)}
down_revision: Union[str, None] = ${repr(down_revision)}
branch_labels: Union[str, Sequence[str], None] = ${repr(branch_labels)}
depends_on: Union[str, Sequence[str], None] = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
