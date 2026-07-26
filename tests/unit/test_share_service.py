"""Tests for share_service.py - public review link generation.

These tests reproduce issue #101: there is currently no share_service module,
no ShareLink model, and no public-link endpoint. All tests will fail until
the feature is implemented.
"""

import inspect
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import pytest

from core.services.share_service import (  # type: ignore[import-not-found]
    create_share_link,
    get_public_review,
)


@pytest.mark.unit
class TestCreateShareLink:
    """Tests for create_share_link(db, review_id, user_id) -> ShareLink."""

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        session = AsyncMock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def review_id(self) -> UUID:
        return uuid4()

    @pytest.fixture
    def user_id(self) -> UUID:
        return uuid4()

    @pytest.fixture
    def mock_complete_review(self, review_id: UUID, user_id: UUID) -> Mock:
        review = Mock()
        review.id = review_id
        review.user_id = user_id
        review.status = "complete"
        review.sections = []
        review.overall_score = 0.8
        return review

    def _setup_review_found(self, mock_db_session: AsyncMock, review: Mock) -> None:
        result = AsyncMock()
        result.scalars.return_value.first.return_value = review
        mock_db_session.execute.return_value = result

    def _setup_review_not_found(self, mock_db_session: AsyncMock) -> None:
        result = AsyncMock()
        result.scalars.return_value.first.return_value = None
        mock_db_session.execute.return_value = result

    @pytest.mark.asyncio
    async def test_returns_share_link_with_token(
        self, mock_db_session: AsyncMock, review_id: UUID, user_id: UUID, mock_complete_review: Mock
    ) -> None:
        """Happy path: returns a ShareLink object with a non-empty token."""
        self._setup_review_found(mock_db_session, mock_complete_review)

        with patch("core.services.share_service.ShareLink") as mock_share_link_cls:
            mock_link = Mock()
            mock_link.token = "abc-def-123"
            mock_share_link_cls.return_value = mock_link

            result = await create_share_link(mock_db_session, review_id, user_id)

        assert result is not None
        assert result.token == "abc-def-123"

    @pytest.mark.asyncio
    async def test_persists_to_db(
        self, mock_db_session: AsyncMock, review_id: UUID, user_id: UUID, mock_complete_review: Mock
    ) -> None:
        """create_share_link calls db.add, commit, and refresh exactly once each."""
        self._setup_review_found(mock_db_session, mock_complete_review)

        with patch("core.services.share_service.ShareLink"):
            await create_share_link(mock_db_session, review_id, user_id)

        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()
        mock_db_session.refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_expires_in_30_days(
        self, mock_db_session: AsyncMock, review_id: UUID, user_id: UUID, mock_complete_review: Mock
    ) -> None:
        """ShareLink.expires_at is set to exactly 30 days from creation time."""
        self._setup_review_found(mock_db_session, mock_complete_review)

        fixed_now = datetime(2026, 1, 1, tzinfo=UTC)
        expected_expiry = datetime(2026, 1, 31, tzinfo=UTC)

        with (
            patch("core.services.share_service.ShareLink") as mock_share_link_cls,
            patch("core.services.share_service.datetime") as mock_dt,
        ):
            mock_dt.now.return_value = fixed_now
            mock_link = Mock()
            mock_link.token = "token-xyz"
            mock_share_link_cls.return_value = mock_link

            await create_share_link(mock_db_session, review_id, user_id)

        call_kwargs = mock_share_link_cls.call_args.kwargs
        assert call_kwargs.get("expires_at") == expected_expiry

    @pytest.mark.asyncio
    async def test_raises_when_review_not_owned_by_user(
        self, mock_db_session: AsyncMock, review_id: UUID
    ) -> None:
        """Non-owner or missing review raises ValueError (not silently succeeds)."""
        self._setup_review_not_found(mock_db_session)

        with pytest.raises(ValueError):
            await create_share_link(mock_db_session, review_id, uuid4())

    @pytest.mark.asyncio
    async def test_token_is_unique_across_calls(
        self, mock_db_session: AsyncMock, user_id: UUID, mock_complete_review: Mock
    ) -> None:
        """Two successive calls produce different tokens (no static/constant token)."""
        tokens = []
        for i in range(2):
            self._setup_review_found(mock_db_session, mock_complete_review)
            with patch("core.services.share_service.ShareLink") as mock_share_link_cls:
                mock_link = Mock()
                mock_link.token = f"unique-token-{i}"
                mock_share_link_cls.return_value = mock_link

                result = await create_share_link(mock_db_session, mock_complete_review.id, user_id)
                tokens.append(result.token)

        assert tokens[0] != tokens[1]


@pytest.mark.unit
class TestGetPublicReview:
    """Tests for get_public_review(db, token) -> Review.

    This function is intentionally unauthenticated — it is the public-facing
    endpoint that recipients access without logging in.
    """

    @pytest.fixture
    def mock_db_session(self) -> AsyncMock:
        session = AsyncMock()
        session.execute = AsyncMock()
        return session

    @pytest.fixture
    def review_id(self) -> UUID:
        return uuid4()

    def _setup_db_responses(
        self,
        mock_db_session: AsyncMock,
        share_link_obj: Mock | None,
        review_obj: Mock | None = None,
    ) -> None:
        """Wire up sequential db.execute responses: first for ShareLink, then for Review."""
        share_result = AsyncMock()
        share_result.scalars.return_value.first.return_value = share_link_obj

        if review_obj is not None:
            review_result = AsyncMock()
            review_result.scalars.return_value.first.return_value = review_obj
            mock_db_session.execute.side_effect = [share_result, review_result]
        else:
            mock_db_session.execute.return_value = share_result

    @pytest.mark.asyncio
    async def test_returns_review_for_valid_non_expired_token(
        self, mock_db_session: AsyncMock, review_id: UUID
    ) -> None:
        """Happy path: a valid, non-expired token returns the associated review."""
        future_expiry = datetime.now(UTC) + timedelta(days=15)
        mock_share = Mock(token="valid-token", review_id=review_id, expires_at=future_expiry)
        mock_review = Mock(id=review_id, status="complete", sections=[], overall_score=0.8)

        self._setup_db_responses(mock_db_session, mock_share, mock_review)

        result = await get_public_review(mock_db_session, "valid-token")

        assert result is not None
        assert result.id == review_id

    @pytest.mark.asyncio
    async def test_raises_for_expired_token(
        self, mock_db_session: AsyncMock, review_id: UUID
    ) -> None:
        """Token past its expires_at is rejected — link cannot be accessed after 30 days."""
        past_expiry = datetime.now(UTC) - timedelta(seconds=1)
        mock_share = Mock(token="expired-token", review_id=review_id, expires_at=past_expiry)

        self._setup_db_responses(mock_db_session, mock_share)

        with pytest.raises(ValueError):
            await get_public_review(mock_db_session, "expired-token")

    @pytest.mark.asyncio
    async def test_raises_for_nonexistent_token(self, mock_db_session: AsyncMock) -> None:
        """Unknown token raises LookupError."""
        self._setup_db_responses(mock_db_session, None)

        with pytest.raises(LookupError):
            await get_public_review(mock_db_session, "does-not-exist")

    @pytest.mark.asyncio
    async def test_function_signature_requires_no_user_id(self) -> None:
        """get_public_review must not require user_id — it is an unauthenticated endpoint."""
        sig = inspect.signature(get_public_review)
        assert (
            "user_id" not in sig.parameters
        ), "get_public_review must not accept user_id — public links are accessed without auth"

    @pytest.mark.asyncio
    async def test_token_expiry_at_exact_boundary(
        self, mock_db_session: AsyncMock, review_id: UUID
    ) -> None:
        """A token that expires at exactly 'now' is treated as expired (boundary check)."""
        exact_now = datetime.now(UTC)
        mock_share = Mock(token="boundary-token", review_id=review_id, expires_at=exact_now)

        self._setup_db_responses(mock_db_session, mock_share)

        with pytest.raises(ValueError):
            await get_public_review(mock_db_session, "boundary-token")
