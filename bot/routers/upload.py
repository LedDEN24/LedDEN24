import os
import re
import uuid
import zipfile
import tempfile
from pathlib import Path
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from django.core.files.base import ContentFile
from asgiref.sync import sync_to_async

from bot.config import is_admin
from bot.keyboards.inline import upload_categories_kb, products_by_category_kb, upload_manage_kb, upload_clear_confirm_kb
from apps.catalog.models import Product, ProductImage
from apps.content.models import GalleryPhoto

router = Router()


@sync_to_async
def _get_product_by_slug(slug: str):
    return Product.objects.filter(slug=slug).first()

@sync_to_async
def _product_images_count_and_last_id(product: Product):
    cnt = ProductImage.objects.filter(product=product).count()
    last = ProductImage.objects.filter(product=product).order_by('-sort', '-id').first()
    return cnt, (last.id if last else None)


@sync_to_async
def _get_product_image_with_product(image_id: int):
    return ProductImage.objects.select_related("product").filter(id=image_id).first()


@sync_to_async
def _get_last_product_image(product: Product):
    return ProductImage.objects.filter(product=product).order_by("-sort", "-id").first()


@sync_to_async
def _get_last_product_image_by_sort(product: Product):
    return ProductImage.objects.filter(product=product).order_by("-sort").first()


@sync_to_async
def _create_product_image(product: Product, sort: int, filename: str, content: bytes):
    img = ProductImage(product=product, sort=sort)
    img.image.save(filename, ContentFile(content), save=True)
    return img.id


@sync_to_async
def _create_gallery_photo(filename: str, content: bytes):
    gp = GalleryPhoto()
    gp.image.save(filename, ContentFile(content), save=True)
    return gp.id


@sync_to_async
def _export_product_images_to_zip(slug: str) -> tuple[bool, str, str | None, int]:
    product = Product.objects.filter(slug=slug).first()
    if not product:
        return False, "Товар не найден.", None, 0

    images = list(ProductImage.objects.filter(product=product).order_by("sort", "id"))
    sources: list[tuple[str, bytes]] = []

    if product.image:
        try:
            with product.image.open("rb") as f:
                ext = os.path.splitext(product.image.name)[1] or ".jpg"
                sources.append((f"00-main{ext}", f.read()))
        except Exception:
            pass

    for idx, img in enumerate(images, start=1):
        if not img.image:
            continue
        try:
            with img.image.open("rb") as f:
                ext = os.path.splitext(img.image.name)[1] or ".jpg"
                sources.append((f"{idx:02d}-gallery{ext}", f.read()))
        except Exception:
            continue

    if not sources:
        return False, "У товара нет файловых фото для выгрузки.", None, 0

    export_dir = Path(tempfile.mkdtemp(prefix="tg_export_"))
    safe_slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", product.slug or "product").strip("-") or "product"
    zip_path = export_dir / f"{safe_slug}-photos.zip"

    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in sources:
            zf.writestr(name, data)

    return True, f"Собрал архив фото товара: {product.title}", str(zip_path), len(sources)


@sync_to_async
def _set_product_main_image(product: Product, filename: str, content: bytes) -> tuple[bool, str]:
    try:
        product.image.save(filename, ContentFile(content), save=True)
        product.save(update_fields=["image", "image_url"])
        return True, "Главное фото сохранено ✅"
    except Exception as e:
        return False, f"Не удалось сохранить главное фото: {e}"


@sync_to_async
def _clear_all_product_images_by_slug(slug: str) -> tuple[bool, str]:
    p = Product.objects.filter(slug=slug).first()
    if not p:
        return False, "Товар не найден."

    deleted = 0
    qs = ProductImage.objects.filter(product=p)
    for img in qs:
        if img.image:
            try:
                img.image.delete(save=False)
            except Exception:
                pass
        img.delete()
        deleted += 1

    had_main = bool(p.image or p.image_url)
    if p.image:
        try:
            p.image.delete(save=False)
        except Exception:
            pass
    p.image = None
    p.image_url = ""
    p.save(update_fields=["image", "image_url"])
    if had_main:
        deleted += 1

    if not deleted:
        return False, "У товара нет фото для удаления."
    return True, f"Очистил все фото товара ✅ Удалено: {deleted}"


@sync_to_async
def _product_has_main_image(product: Product) -> bool:
    return bool(product.image or product.image_url)


@sync_to_async
def _product_images_count(product: Product) -> int:
    return ProductImage.objects.filter(product=product).count()


@sync_to_async
def _get_product_title(slug: str) -> str | None:
    p = Product.objects.filter(slug=slug).only("title").first()
    return p.title if p else None


@sync_to_async
def _make_main_from_image(image_id: int) -> tuple[bool, str]:
    """Copy ProductImage -> Product main image (sync storage ops)."""
    im = ProductImage.objects.select_related("product").filter(id=int(image_id)).first()
    if not im:
        return False, "Фото не найдено."
    p = im.product
    if im.image:
        try:
            with im.image.open("rb") as f:
                data = f.read()
            ext = os.path.splitext(im.image.name)[1] or ".jpg"
            p.image.save(f"{p.slug}-main{ext}", ContentFile(data), save=True)
            p.save(update_fields=["image", "image_url"])
            return True, "Готово ✅ Это фото теперь главное."
        except Exception as e:
            return False, f"Не удалось сделать главным: {e}"
    if im.image_url:
        p.image_url = im.image_url
        p.save(update_fields=["image_url"])
        return True, "Готово ✅ Это фото теперь главное."
    return False, "У этого фото нет файла/URL."


@sync_to_async
def _delete_last_image_by_product_slug(slug: str) -> tuple[bool, str]:
    p = Product.objects.filter(slug=slug).first()
    if not p:
        return False, "Товар не найден."
    last = ProductImage.objects.filter(product=p).order_by("-sort", "-id").first()
    if not last:
        return False, "Нет фото для удаления."
    if last.image:
        try:
            last.image.delete(save=False)
        except Exception:
            pass
    last.delete()
    cnt = ProductImage.objects.filter(product=p).count()
    return True, f"Удалил последнее фото ✅ Осталось: {cnt}"

class UploadFlow(StatesGroup):
    picking_category = State()
    picking_product = State()
    waiting_product_photos = State()
    waiting_gallery_photos = State()
    waiting_main_photo = State()

@router.callback_query(F.data == "noop")
async def noop(c: CallbackQuery):
    await c.answer()

# --- Upload product photos (admin) ---
@router.message(Command("upload"))
async def upload_cmd(m: Message, state: FSMContext):
    """/upload — выбор категории -> товара кнопками. /upload <slug> тоже работает."""
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return

    parts = (m.text or "").split(maxsplit=1)
    if len(parts) >= 2:
        slug = parts[1].strip()
        p = await _get_product_by_slug(slug)
        if not p:
            await m.answer("Товар не найден. Можно вызвать /upload и выбрать кнопкой.")
            return
        await state.update_data(product_slug=slug, count=0)
        await state.set_state(UploadFlow.waiting_product_photos)
        await m.answer(f"Ок. Пришли фото для товара: {p.title}\nМожно 4–6 фото одним альбомом или по одному.\nКогда закончишь — /done\nУправление фото: /manage")
        return

    await state.set_state(UploadFlow.picking_category)
    await m.answer("Выбери категорию:", reply_markup=await upload_categories_kb())

@router.callback_query(UploadFlow.picking_category, F.data.startswith("upl_cat:"))
async def pick_category(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    cat = c.data.split(":",1)[1]
    await state.update_data(upload_cat=cat)
    await state.set_state(UploadFlow.picking_product)
    await c.message.edit_text("Выбери товар:", reply_markup=await products_by_category_kb(cat, page=1))
    await c.answer()

@router.callback_query(UploadFlow.picking_product, F.data.startswith("upl_pcat:"))
async def products_page_in_cat(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    _, cat, page = c.data.split(":",2)
    await c.message.edit_reply_markup(reply_markup=await products_by_category_kb(cat, page=int(page)))
    await c.answer()

@router.callback_query(UploadFlow.picking_product, F.data == "upl_back_cats")
async def back_to_cats(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    await state.set_state(UploadFlow.picking_category)
    await c.message.edit_text("Выбери категорию:", reply_markup=await upload_categories_kb())
    await c.answer()

@router.callback_query(UploadFlow.picking_category, F.data == "upl_cancel")
@router.callback_query(UploadFlow.picking_product, F.data == "upl_cancel")
async def upl_cancel(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    await state.clear()
    await c.message.answer("Отменено.")
    await c.answer()

@router.callback_query(UploadFlow.picking_product, F.data.startswith("upl_pick:"))
async def upl_pick(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":",1)[1]
    p = await _get_product_by_slug(slug)
    if not p:
        await c.message.answer("Товар не найден.")
        await c.answer()
        return
    await state.update_data(product_slug=slug, count=0)
    await state.set_state(UploadFlow.waiting_product_photos)
    await c.message.answer(f"Ок. Пришли фото для товара: {p.title}\nМожно 4–6 фото одним альбомом или по одному.\nКогда закончишь — /done\nУправление фото: /manage")
    await c.answer()

@router.message(Command("manage"))
async def manage_cmd(m: Message, state: FSMContext):
    """Показывает кнопки управления фото выбранного товара."""
    if not is_admin(m.from_user.id):
        return
    data = await state.get_data()
    slug = data.get("product_slug")
    if not slug:
        await m.answer("Сначала выбери товар через /upload (или /upload <slug>).")
        return
    p = await _get_product_by_slug(slug)
    if not p:
        await m.answer("Товар не найден.")
        return
    cnt, last_id = await _product_images_count_and_last_id(p)
    await m.answer(
        f"Управление фото товара: {p.title}\nСейчас фото: {cnt}",
        reply_markup=upload_manage_kb(p.slug, last_image_id=last_id),
    )



@router.message(Command("export_photos"))
async def export_photos_cmd(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return

    parts = (m.text or "").split(maxsplit=1)
    slug = None
    if len(parts) >= 2:
        slug = parts[1].strip()
    else:
        data = await state.get_data()
        slug = data.get("product_slug")

    if not slug:
        await m.answer("Укажи slug: /export_photos <slug> или сначала выбери товар через /upload.")
        return

    ok, msg, zip_path, total = await _export_product_images_to_zip(slug)
    if not ok or not zip_path:
        await m.answer(msg)
        return

    try:
        await m.answer_document(FSInputFile(zip_path), caption=f"{msg}\nФайлов в архиве: {total}")
    except Exception as e:
        await m.answer(f"Не удалось отправить архив в Telegram: {e}")
    finally:
        try:
            os.remove(zip_path)
            Path(zip_path).parent.rmdir()
        except Exception:
            pass


@router.callback_query(F.data.startswith("upl_upload_main:"))
async def upl_upload_main(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":",1)[1]
    p = await _get_product_by_slug(slug)
    if not p:
        await c.message.answer("Товар не найден.")
        await c.answer(); return
    await state.update_data(main_product_slug=slug)
    await state.set_state(UploadFlow.waiting_main_photo)
    await c.message.answer(f"Пришли ОДНО фото, я поставлю его главным для: {p.title}\n(Отмена: /cancel)")
    await c.answer()

@router.callback_query(F.data.startswith("upl_make_main:"))
async def make_main(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    image_id = int(c.data.split(":",1)[1])
    ok, msg = await _make_main_from_image(image_id)
    await c.message.answer(msg)
    await c.answer()

@router.callback_query(F.data.startswith("upl_del_last:"))
async def del_last(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":",1)[1]
    ok, msg = await _delete_last_image_by_product_slug(slug)
    await c.message.answer(msg)
    await c.answer()


@router.callback_query(F.data.startswith("upl_clear_ask:"))
async def clear_all_ask(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":",1)[1]
    title = await _get_product_title(slug)
    if not title:
        await c.message.answer("Товар не найден.")
        await c.answer(); return
    await c.message.answer(
        f"Удалить все дополнительные фото у товара: {title}?",
        reply_markup=upload_clear_confirm_kb(slug),
    )
    await c.answer()


@router.callback_query(F.data.startswith("upl_clear_yes:"))
async def clear_all_yes(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":",1)[1]
    ok, msg = await _clear_all_product_images_by_slug(slug)
    await c.message.answer(msg)
    await c.answer()


@router.callback_query(F.data == "upl_clear_no")
async def clear_all_no(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    await c.message.answer("Очистка отменена.")
    await c.answer()


@router.callback_query(F.data.startswith("upl_export_zip:"))
async def export_product_zip(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    slug = c.data.split(":", 1)[1]
    ok, msg, zip_path, total = await _export_product_images_to_zip(slug)
    if not ok or not zip_path:
        await c.message.answer(msg)
        await c.answer()
        return

    try:
        await c.message.answer_document(
            FSInputFile(zip_path),
            caption=f"{msg}\nФайлов в архиве: {total}",
        )
    except Exception as e:
        await c.message.answer(f"Не удалось отправить архив в Telegram: {e}")
    finally:
        try:
            os.remove(zip_path)
            Path(zip_path).parent.rmdir()
        except Exception:
            pass

    await c.answer()


@router.message(Command("done"))
async def done_cmd(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    data = await state.get_data()
    if data.get("product_slug") or data.get("gcount") is not None:
        await state.clear()
        await m.answer("Готово ✅ Фото сохранены.")
        return
    await m.answer("Нет активной загрузки. Используй /upload или /upload_gallery.")

@router.message(Command("cancel"))
async def cancel_cmd(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        return
    await state.clear()
    await m.answer("Отменено.")

@router.message(UploadFlow.waiting_product_photos, F.photo)
async def receive_product_photo(m: Message, bot: Bot, state: FSMContext):
    if not is_admin(m.from_user.id):
        return

    data = await state.get_data()
    slug = data.get("product_slug")
    if not slug:
        await m.answer("Сначала /upload и выбери товар.")
        return

    product = await _get_product_by_slug(slug)
    if not product:
        await m.answer("Товар не найден.")
        await state.clear()
        return

    ph = m.photo[-1]
    try:
        file = await bot.get_file(ph.file_id)
        stream = await bot.download_file(file.file_path)
        content = stream.read()
    except Exception as e:
        await m.answer(f"Не удалось скачать фото из Telegram: {e}")
        return

    last = await _get_last_product_image_by_sort(product)
    next_sort = (last.sort + 1) if last else 0

    ext = os.path.splitext(file.file_path)[1] or ".jpg"
    unique_suffix = uuid.uuid4().hex[:8]
    fname = f"{product.slug}-{next_sort}-{unique_suffix}{ext}"
    await _create_product_image(product, next_sort, fname, content)

    if not await _product_has_main_image(product):
        await _set_product_main_image(product, f"{product.slug}-main-{unique_suffix}{ext}", content)

    count = int(data.get("count") or 0) + 1
    total = await _product_images_count(product)
    await state.update_data(count=count)
    await m.answer(
        f"Сохранено фото товара #{count} ✅\n"
        f"Всего дополнительных фото у товара: {total}\n"
        "Можно отправить ещё несколько фото подряд или альбомом. Когда закончишь — /done\n"
        "Управление фото: /manage"
    )


@router.message(UploadFlow.waiting_product_photos)
async def receive_product_photo_invalid(m: Message):
    if not is_admin(m.from_user.id):
        return
    await m.answer("Сейчас жду фото товара. Можно прислать несколько фото подряд или одним альбомом. Завершить — /done")


@router.message(UploadFlow.waiting_main_photo, F.photo)
async def receive_main_photo(m: Message, bot: Bot, state: FSMContext):
    if not is_admin(m.from_user.id):
        return

    data = await state.get_data()
    slug = data.get("main_product_slug")
    if not slug:
        await m.answer("Не выбран товар для главного фото. Сначала /manage.")
        await state.clear()
        return

    product = await _get_product_by_slug(slug)
    if not product:
        await m.answer("Товар не найден.")
        await state.clear()
        return

    ph = m.photo[-1]
    try:
        file = await bot.get_file(ph.file_id)
        stream = await bot.download_file(file.file_path)
        content = stream.read()
    except Exception as e:
        await m.answer(f"Не удалось скачать фото из Telegram: {e}")
        return

    ext = os.path.splitext(file.file_path)[1] or ".jpg"
    unique_suffix = uuid.uuid4().hex[:8]
    ok, msg = await _set_product_main_image(product, f"{product.slug}-main-{unique_suffix}{ext}", content)
    await state.clear()
    await m.answer(msg)


@router.message(UploadFlow.waiting_main_photo)
async def receive_main_photo_invalid(m: Message):
    if not is_admin(m.from_user.id):
        return
    await m.answer("Сейчас жду одно фото для главного изображения товара. Отмена — /cancel")


# --- Upload gallery photos ---
@router.message(Command("upload_gallery"))
async def upload_gallery_cmd(m: Message, state: FSMContext):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    await state.update_data(gcount=0)
    await state.set_state(UploadFlow.waiting_gallery_photos)
    await m.answer("Ок. Пришли фото для галереи магазина (можно альбомом).\nКогда закончишь — /done\nЧтобы отменить — /cancel")

@router.message(UploadFlow.waiting_gallery_photos, F.photo)
async def receive_gallery_photo(m: Message, bot: Bot, state: FSMContext):
    if not is_admin(m.from_user.id):
        return

    try:
        ph = m.photo[-1]
        file = await bot.get_file(ph.file_id)
        stream = await bot.download_file(file.file_path)
        content = stream.read()
    except Exception as e:
        await m.answer(f"Не удалось скачать фото из Telegram: {e}")
        return

    ext = os.path.splitext(file.file_path)[1] or ".jpg"
    data = await state.get_data()
    gcount = int(data.get("gcount") or 0)
    fname = f"gallery-{uuid.uuid4().hex[:12]}{ext}"

    await _create_gallery_photo(fname, content)

    gcount += 1
    await state.update_data(gcount=gcount)
    await m.answer(f"Сохранено фото галереи #{gcount} ✅ Можно прислать ещё несколько фото или /done")


@router.message(UploadFlow.waiting_gallery_photos)
async def receive_gallery_photo_invalid(m: Message):
    if not is_admin(m.from_user.id):
        return
    await m.answer("Сейчас жду фото для галереи. Можно прислать несколько фото подряд или альбомом. Завершить — /done")
