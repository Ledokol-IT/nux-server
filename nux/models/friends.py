from __future__ import annotations
import datetime
import typing as t
from collections import defaultdict

from loguru import logger
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


def remove_invite(
        session: orm.Session,
        from_user: muser.User,
        to_user: muser.User,
) -> bool:
    """Return True if invite found and deleted. False otherwise"""
    invite = find_invite(session, from_user, to_user)
    if invite:
        session.delete(invite)
        return True
    else:
        return False


def remove_friendship(
        session: orm.Session,
        current_user: muser.User,
        friend: muser.User,
) -> bool:
    """Return True if friendship found and deleted. False otherwise"""
    friendship = find_friendship(session, current_user, friend)
    if friendship:
        session.delete(friendship)
        return True
    else:
        return False


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
    limit: int | None = None,
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
    if limit is not None:
        query = query.limit(limit)

    friends = query.all()

    return friends


def get_recommended_friends(
    session: orm.Session,
    user: muser.User,
) -> list[muser.User]:
    friends = get_friends(session, user, limit=100)
    recommended: defaultdict[muser.User, int] = defaultdict(lambda: 0)
    for friend in friends:
        for two_edge_friend in get_friends(session, friend, limit=100):
            recommended[two_edge_friend] += 1
    for friend in friends:
        recommended.pop(friend, None)
    recommended.pop(user, None)
    recommended_list = sorted(recommended.items(), key=lambda t: t[1], reverse=True)
    return [user for user, _ in recommended_list]
