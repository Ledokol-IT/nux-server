from __future__ import annotations
import datetime
import typing as t

import sqlalchemy as sa
from sqlalchemy import orm

import nux.database
import nux.events
import nux.models.status as mstatus
import nux.models.user as muser
from nux.utils import now

from nux.schemes import PendingFriendsInviteScheme, OutgoingFriendsInviteScheme


class FriendsInvite(nux.database.Base):
    __tablename__ = "friends_invites"

    from_user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    from_user: muser.User = orm.relationship(
        lambda: muser.User,
        back_populates="outgoing_friends_invites",
        foreign_keys=[from_user_id],
    )

    to_user_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    to_user: muser.User = orm.relationship(
        lambda: muser.User,
        back_populates="pending_friends_invites",
        foreign_keys=[to_user_id],
    )

    dt_sent: datetime.datetime = sa.Column(
        sa.DateTime,
        nullable=False,
    )  # type: ignore


class Friendship(nux.database.Base):
    __tablename__ = "friendships"

    user1_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    user1: muser.User = orm.relationship(
        lambda: muser.User,
        back_populates="_friendships1",
        foreign_keys=[user1_id],
    )

    user2_id: str = sa.Column(
        sa.String,
        sa.ForeignKey("users.id"),
        primary_key=True,
    )  # type: ignore

    user2: muser.User = orm.relationship(
        lambda: muser.User,
        back_populates="_friendships2",
        foreign_keys=[user2_id],
    )


def find_invite(
        session: orm.Session,
        from_user: muser.User,
        to_user: muser.User,
) -> FriendsInvite | None:
    return session.query(FriendsInvite).where(
        sa.and_(
            FriendsInvite.from_user_id == from_user.id,
            FriendsInvite.to_user_id == to_user.id,
        )
    ).first()


def create_invite(
        session: orm.Session,
        from_user: muser.User,
        to_user: muser.User,
):
    invite = FriendsInvite()
    invite.from_user = from_user
    invite.to_user = to_user
    invite.dt_sent = now()
    session.add(invite)
    return invite


def create_friendship(
        session: orm.Session,
        user1: muser.User,
        user2: muser.User,
):
    friendship = Friendship()
    friendship.user1 = user1
    friendship.user2 = user2
    session.add(friendship)


def find_friendship(
        session: orm.Session,
        user1: muser.User,
        user2: muser.User,
):
    return session.query(Friendship).where(
        sa.or_(
            sa.and_(
                Friendship.user1_id == user1.id,
                Friendship.user2_id == user2.id,
            ),
            sa.and_(
                Friendship.user1_id == user2.id,
                Friendship.user2_id == user1.id,
            ),
        )
    ).first()


def add_user_as_friend(
        session: orm.Session,
        events: nux.events.NuxEvents | None,
        from_user: muser.User,
        to_user: muser.User,
):
    if from_user == to_user:
        raise AttributeError(f"{to_user=!r} == {from_user=!r}")
    if find_friendship(session, from_user, to_user):
        return
    elif find_invite(session, from_user, to_user):
        return
    elif invite := find_invite(session, to_user, from_user):
        session.delete(invite)
        create_friendship(session, from_user, to_user)
        if events:
            events.accept_friends_invite(session, from_user, to_user)
    else:
        create_invite(session, from_user, to_user)
        if events:
            events.friends_invite(session, from_user, to_user)


def get_pending_friends_invites(
        session: orm.Session,
        to_user: muser.User,
):
    _ = session
    return to_user.pending_friends_invites


def get_outgoing_friends_invites(
        session: orm.Session,
        to_user: muser.User,
):
    _ = session
    return to_user.outgoing_friends_invites


def get_friends(
    session: orm.Session,
    user: muser.User,
    order: t.Literal["online"] | None = None,
) -> list[muser.User]:
    query = (
        session.query(muser.User)
        .where(
            sa.or_(
                sa.and_(
                    Friendship.user1_id == user.id,
                    Friendship.user2_id == muser.User.id,
                ),
                sa.and_(
                    Friendship.user1_id == muser.User.id,
                    Friendship.user2_id == user.id,
                ),
            )
        )
    )
    if order == "online":
        query = (
            query
            .join(muser.User.status)
            .order_by(mstatus.UserStatus.dt_last_update)
            .order_by(mstatus.UserStatus.online)
            .order_by(mstatus.UserStatus.in_app)
        )

    friends = query.all()

    return friends
