"""
Script de migração única: converte .docx / .pdf / .txt → .md com frontmatter YAML.

Uso:
    python migrate.py                          # usa CIFRAS_ROOT do .env
    python migrate.py --dry-run                # lista o que seria convertido, sem gravar
    python migrate.py --source C:\...\Cifras --dest C:\...\Cifras_md
"""

import argparse
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from app import extract_text, CIFRAS_ROOT, SUPPORTED_EXTENSIONS


def slugify(text):
    """Remove caracteres inválidos para nome de arquivo."""
    return re.sub(r'[<>:"/\\|?*]', '_', text).strip()


def build_frontmatter(title, section, category):
    cat_display = "" if category == "_raiz" else category
    return (
        "---\n"
        f"title: {title}\n"
        "artist: \n"
        "key: \n"
        f"section: {section}\n"
        f"category: {cat_display}\n"
        "tags: []\n"
        "---\n\n"
    )


def migrate(source_root, dest_root, dry_run=False):
    source = Path(source_root).resolve()
    dest = Path(dest_root).resolve()

    if not source.exists():
        print(f"[ERRO] Pasta de origem não encontrada: {source}")
        sys.exit(1)

    if dest == source:
        print("[ERRO] Pasta de destino deve ser diferente da origem.")
        sys.exit(1)

    converted = 0
    errors = 0

    for section_dir in sorted(source.iterdir()):
        if not section_dir.is_dir():
            continue
        section = section_dir.name

        for item in sorted(section_dir.rglob("*")):
            if not item.is_file():
                continue
            if item.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            # Categoria = pasta imediatamente abaixo da seção
            rel = item.relative_to(section_dir)
            category = rel.parts[0] if len(rel.parts) > 1 else "_raiz"

            title = item.stem
            out_dir = dest / section / (category if category != "_raiz" else "")
            out_file = out_dir / (slugify(title) + ".md")

            rel_in = item.relative_to(source)
            rel_out = out_file.relative_to(dest)
            print(f"  {'[DRY] ' if dry_run else ''}{rel_in}  →  {rel_out}")

            if dry_run:
                converted += 1
                continue

            out_dir.mkdir(parents=True, exist_ok=True)

            text = extract_text(str(item))
            if text.startswith("[Erro"):
                print(f"    [AVISO] {text}")
                errors += 1

            content = build_frontmatter(title, section, category) + text

            try:
                out_file.write_text(content, encoding="utf-8")
                converted += 1
            except Exception as e:
                print(f"    [ERRO] Não foi possível salvar: {e}")
                errors += 1

    status = "[DRY RUN] " if dry_run else ""
    print(f"\n{status}Concluído: {converted} arquivo(s) convertido(s), {errors} erro(s).")
    print(f"Destino: {dest}")


if __name__ == "__main__":
    default_dest = str(Path(CIFRAS_ROOT).parent / (Path(CIFRAS_ROOT).name + "_md"))

    parser = argparse.ArgumentParser(description="Migra cifras existentes para .md com frontmatter")
    parser.add_argument("--source", default=CIFRAS_ROOT, help=f"Pasta de origem (padrão: {CIFRAS_ROOT})")
    parser.add_argument("--dest", default=default_dest, help=f"Pasta de destino (padrão: {default_dest})")
    parser.add_argument("--dry-run", action="store_true", help="Lista arquivos sem converter")
    args = parser.parse_args()

    print(f"Origem : {args.source}")
    print(f"Destino: {Path(args.dest).resolve()}")
    print(f"Modo   : {'DRY RUN (nada será gravado)' if args.dry_run else 'MIGRAÇÃO REAL'}\n")

    if not args.dry_run:
        resp = input("Confirmar migração? [s/N] ").strip().lower()
        if resp != "s":
            print("Cancelado.")
            sys.exit(0)

    migrate(args.source, args.dest, args.dry_run)
