from aiogram.utils.i18n import gettext as _
from aiogram import Router
from bot.filters.admins import AdminFilter


no_access_router = Router()
no_access_router.callback_query.filter(AdminFilter(admin_right=''))


@no_access_router.callback_query(AdminFilter(''))
async def currencies_update_function(callback_query, state):
    await callback_query.answer(_("⚠️ У вас нет прав на данное действие"), show_alert=True)
