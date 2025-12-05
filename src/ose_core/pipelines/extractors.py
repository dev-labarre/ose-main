"""
Extractor components for the fast pipeline.

These classes perform vectorized extraction of companies, articles, and projects
from JSONL records, producing the nine datasets expected by the project.
"""

from typing import Any, Dict, Iterator, List

import pandas as pd


def safe_join(items: Any, separator: str = ", ") -> str:
    """Safely join list items, handling dicts and other types."""
    if not isinstance(items, list):
        return str(items) if items else ""
    result = []
    for item in items:
        if isinstance(item, dict):
            if "label" in item:
                result.append(str(item["label"]))
            elif "name" in item:
                result.append(str(item["name"]))
            else:
                result.append(str(item))
        else:
            result.append(str(item))
    return separator.join(result)


def format_siret(siret: Any) -> str:
    """Format SIRET as 14-digit string."""
    if pd.isna(siret) or siret == "" or siret == "nan":
        return ""
    try:
        if isinstance(siret, (int, float)):
            return f"{int(siret):014d}"
        val_str = str(siret).strip()
        if val_str and val_str != "nan":
            try:
                return f"{int(float(val_str)):014d}"
            except Exception:
                return val_str
        return ""
    except Exception:
        return str(siret) if siret else ""


class VectorizedArticleExtractor:
    """Extract article datasets using vectorized operations."""

    def __init__(self) -> None:
        self.articles_list: List[pd.DataFrame] = []

    def extract_chunk(self, chunk_df: pd.DataFrame) -> None:
        """Extract data from an article DataFrame chunk."""
        articles_expanded = []

        def safe_get_list(value, default=None):
            try:
                if value is None:
                    return default
                if isinstance(value, pd.Series):
                    if len(value) == 0:
                        return default
                    try:
                        if value.isna().all():
                            return default
                    except (ValueError, TypeError):
                        pass
                    if len(value) == 1:
                        val = value.iloc[0]
                        try:
                            if pd.isna(val):
                                return default
                        except (ValueError, TypeError):
                            pass
                        if isinstance(val, list):
                            return val if len(val) > 0 else default
                        return default
                    return value.tolist()
                try:
                    if pd.isna(value):
                        return default
                except (ValueError, TypeError):
                    pass
                if isinstance(value, list):
                    return value if len(value) > 0 else default
                if hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                    try:
                        value_list = list(value)
                        if len(value_list) == 0:
                            return default
                        return value_list
                    except (ValueError, TypeError):
                        return default
                return default
            except (ValueError, TypeError, AttributeError):
                return default

        for _, row in chunk_df.iterrows():
            companies = safe_get_list(row.get("companies"))
            if not companies:
                companies = safe_get_list(row.get("all_companies"))

            if not companies:
                companies = []

            if not companies:
                base_index = {"company_name": "", "siren": "", "siret": ""}
                articles_expanded.append(self._create_article_row(row, base_index))
            else:
                for company in companies:
                    if isinstance(company, dict):
                        base_index = {
                            "company_name": company.get("label", ""),
                            "siren": str(company.get("siren", "")),
                            "siret": format_siret(company.get("siret", "")),
                        }
                    else:
                        base_index = {"company_name": "", "siren": "", "siret": ""}
                    articles_expanded.append(self._create_article_row(row, base_index))

        if articles_expanded:
            self.articles_list.append(pd.DataFrame(articles_expanded))

    def _create_article_row(self, row: pd.Series, base_index: Dict[str, str]) -> Dict[str, Any]:
        """Create an article row with base index."""
        author_name = ""
        author_val = row.get("author")
        try:
            if not pd.isna(author_val) and isinstance(author_val, dict):
                author_name = author_val.get("name", "")
        except (ValueError, TypeError):
            pass

        country_label = ""
        country_val = row.get("country")
        try:
            if not pd.isna(country_val) and isinstance(country_val, dict):
                country_label = country_val.get("label", "")
        except (ValueError, TypeError):
            pass

        def safe_get_list(value, default=None):
            try:
                if pd.isna(value):
                    return default
                if isinstance(value, list):
                    return value
                if hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                    return list(value)
                return default
            except (ValueError, TypeError):
                return default

        signals_status = safe_get_list(row.get("signalsStatus"), [])
        signals_type = safe_get_list(row.get("signalsType"), [])
        sectors = safe_get_list(row.get("sectors"), [])
        cities = safe_get_list(row.get("cities"), [])
        sources = safe_get_list(row.get("sources"), [])
        departments = safe_get_list(row.get("departments"), [])
        all_companies = safe_get_list(row.get("all_companies"), [])
        companies = safe_get_list(row.get("companies"), [])

        def safe_get_scalar(value, default=""):
            try:
                if pd.isna(value):
                    return default
                return str(value) if value else default
            except (ValueError, TypeError):
                return default

        article_row = base_index.copy()
        article_row.update(
            {
                "title": safe_get_scalar(row.get("title"), ""),
                "publishedAt": safe_get_scalar(row.get("publishedAt"), ""),
                "author": author_name,
                "signalsStatus": safe_join(signals_status),
                "signalsType": safe_join(signals_type),
                "country": country_label,
                "sectors": safe_join(sectors),
                "cities": safe_join(cities),
                "sources": safe_join(sources),
                "departments": safe_join(departments),
                "all_companies_count": len(all_companies),
                "companies_count": len(companies),
            }
        )
        return article_row

    def get_datasets(self) -> Dict[str, pd.DataFrame]:
        """Return extracted datasets."""
        if self.articles_list:
            return {"09_articles": pd.concat(self.articles_list, ignore_index=True)}
        return {"09_articles": pd.DataFrame()}


class VectorizedProjectExtractor:
    """Extract project datasets (mapped to signals) using vectorized operations."""

    def __init__(self) -> None:
        self.signals_list: List[pd.DataFrame] = []

    def extract_chunk(self, chunk_df: pd.DataFrame) -> None:
        """Extract data from a project DataFrame chunk."""
        signals_expanded = []

        def safe_get_list(value, default=None):
            try:
                if value is None:
                    return default
                if isinstance(value, pd.Series):
                    if len(value) == 0:
                        return default
                    try:
                        if value.isna().all():
                            return default
                    except (ValueError, TypeError):
                        pass
                    if len(value) == 1:
                        val = value.iloc[0]
                        try:
                            if pd.isna(val):
                                return default
                        except (ValueError, TypeError):
                            pass
                        if isinstance(val, list):
                            return val if len(val) > 0 else default
                        return default
                    return value.tolist()
                try:
                    if pd.isna(value):
                        return default
                except (ValueError, TypeError):
                    pass
                if isinstance(value, list):
                    return value if len(value) > 0 else default
                if hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                    try:
                        value_list = list(value)
                        if len(value_list) == 0:
                            return default
                        return value_list
                    except (ValueError, TypeError):
                        return default
                return default
            except (ValueError, TypeError, AttributeError):
                return default

        for _, row in chunk_df.iterrows():
            companies = safe_get_list(row.get("companies"))
            if not companies:
                companies = safe_get_list(row.get("companiesmain"))
            if not companies:
                companies = safe_get_list(row.get("allCompanies"))

            sirets = safe_get_list(row.get("sirets"))

            if not companies:
                companies = []
            if not sirets:
                sirets = []

            if not companies and not sirets:
                base_index = {"company_name": "", "siren": "", "siret": ""}
                signals_expanded.append(self._create_signal_row(row, base_index))
            else:
                if companies:
                    for company in companies:
                        if isinstance(company, dict):
                            company_id = company.get("id", "")
                            base_index = {
                                "company_name": "",
                                "siren": str(company_id) if company_id else "",
                                "siret": "",
                            }
                        else:
                            base_index = {
                                "company_name": "",
                                "siren": str(company) if company else "",
                                "siret": "",
                            }
                        signals_expanded.append(self._create_signal_row(row, base_index))

                if sirets:
                    for siret_info in sirets:
                        if isinstance(siret_info, dict):
                            siret = format_siret(siret_info.get("siret", ""))
                        else:
                            siret = format_siret(siret_info)

                        base_index = {
                            "company_name": "",
                            "siren": siret[:9] if len(siret) >= 9 else "",
                            "siret": siret,
                        }
                        signals_expanded.append(self._create_signal_row(row, base_index))

        if signals_expanded:
            self.signals_list.append(pd.DataFrame(signals_expanded))

    def _create_signal_row(self, row: pd.Series, base_index: Dict[str, str]) -> Dict[str, Any]:
        """Create a signal row with base index."""

        def is_not_na(value):
            try:
                return not pd.isna(value)
            except (ValueError, TypeError):
                return False

        def safe_get_list(value, default=None):
            try:
                if not is_not_na(value):
                    return default
                if isinstance(value, list):
                    return value
                if hasattr(value, "__iter__") and not isinstance(value, (str, dict)):
                    return list(value)
                return default
            except (ValueError, TypeError):
                return default

        country_label = ""
        country = row.get("country")
        try:
            if is_not_na(country):
                if isinstance(country, list) and len(country) > 0:
                    if isinstance(country[0], dict):
                        country_label = country[0].get("label", "")
                    else:
                        country_label = str(country[0])
                elif isinstance(country, dict):
                    country_label = country.get("label", "")
        except (ValueError, TypeError):
            pass

        dept_label = ""
        dept = row.get("departement")
        try:
            if is_not_na(dept):
                if isinstance(dept, list) and len(dept) > 0:
                    if isinstance(dept[0], dict):
                        dept_label = dept[0].get("label", "")
                    else:
                        dept_label = str(dept[0])
        except (ValueError, TypeError):
            pass

        type_label = ""
        type_id = ""
        type_val = row.get("type")
        try:
            if is_not_na(type_val) and isinstance(type_val, dict):
                type_label = type_val.get("label", "")
                type_id = type_val.get("id", "")
        except (ValueError, TypeError):
            pass

        statut_label = ""
        statut_val = row.get("statut")
        try:
            if is_not_na(statut_val) and isinstance(statut_val, dict):
                statut_label = statut_val.get("label", "")
        except (ValueError, TypeError):
            pass

        continent = safe_get_list(row.get("continent"), [])
        nature_op = safe_get_list(row.get("natureOp"), [])
        companies = safe_get_list(row.get("companies"), [])
        sirets = safe_get_list(row.get("sirets"), [])

        def safe_get_scalar(value, default=""):
            try:
                if not is_not_na(value):
                    return default
                return str(value) if value else default
            except (ValueError, TypeError):
                return default

        signal_row = base_index.copy()
        signal_row.update(
            {
                "continent": safe_join(continent),
                "country": country_label,
                "departement": dept_label,
                "publishedAt": safe_get_scalar(row.get("publishedAt"), ""),
                "isMain": True,
                "type": type_label,
                "type_id": type_id,
                "createdAt": safe_get_scalar(row.get("createdAt"), ""),
                "statut": statut_label,
                "city_label": safe_get_scalar(row.get("city_label"), ""),
                "city_zip_code": safe_get_scalar(row.get("city_zip_code"), ""),
                "natureOp": safe_join(nature_op),
                "companies_count": len(companies),
                "sirets_count": len(sirets),
            }
        )
        return signal_row

    def get_datasets(self) -> Dict[str, pd.DataFrame]:
        """Return extracted datasets."""
        if self.signals_list:
            return {"08_signals": pd.concat(self.signals_list, ignore_index=True)}
        return {"08_signals": pd.DataFrame()}


class VectorizedCompanyExtractor:
    """Extract company datasets using vectorized operations."""

    def __init__(self) -> None:
        self.dataframes = {
            "01_company_basic_info": [],
            "02_financial_data": [],
            "03_workforce_data": [],
            "04_company_structure": [],
            "05_classification_flags": [],
            "06_contact_metrics": [],
            "07_kpi_data": [],
        }
        self.articles_extractor = VectorizedArticleExtractor()
        self.signals_extractor = VectorizedProjectExtractor()

    def extract_chunk(self, chunk_df: pd.DataFrame) -> None:
        """Extract data from a DataFrame chunk."""

        def safe_get(df: pd.DataFrame, col: str, default=""):
            if col in df.columns:
                return df[col]
            if isinstance(default, str):
                return pd.Series([default] * len(df), dtype=str)
            if isinstance(default, (int, float)):
                return pd.Series([default] * len(df), dtype=type(default))
            if isinstance(default, bool):
                return pd.Series([default] * len(df), dtype=bool)
            if isinstance(default, dict):
                return pd.Series([default] * len(df), dtype=object)
            return pd.Series([default] * len(df), dtype=object)

        # Extract company name with fallback options
        # After pd.json_normalize, socialName should be available directly
        # But handle cases where it might be missing or in a different format
        company_name_series = safe_get(chunk_df, "socialName", "")
        if company_name_series.empty or company_name_series.isna().all():
            # Try alternative column names
            for alt_col in ["label", "name", "raison_sociale"]:
                if alt_col in chunk_df.columns:
                    company_name_series = safe_get(chunk_df, alt_col, "")
                    if not company_name_series.empty and not company_name_series.isna().all():
                        break

        base_index = pd.DataFrame(
            {
                "company_name": company_name_series.fillna(""),
                "siren": safe_get(chunk_df, "siren", "").astype(str).fillna(""),
                "siret": safe_get(chunk_df, "siret", "").apply(format_siret),
            }
        )

        dept_label = safe_get(chunk_df, "department", {})
        dept_label = dept_label.apply(lambda x: x.get("label", "") if isinstance(x, dict) else "")
        dept_id = safe_get(chunk_df, "department", {})
        dept_id = dept_id.apply(lambda x: x.get("id", "") if isinstance(x, dict) else "")

        naf_code = safe_get(chunk_df, "naf", {})
        naf_code = naf_code.apply(lambda x: x.get("code", "") if isinstance(x, dict) else "")
        naf_label = safe_get(chunk_df, "naf", {})
        naf_label = naf_label.apply(lambda x: x.get("label", "") if isinstance(x, dict) else "")

        juridic_form = safe_get(chunk_df, "juridicForm", {})
        juridic_form = juridic_form.apply(lambda x: x.get("label", "") if isinstance(x, dict) else "")

        basic_info = base_index.copy()
        basic_info = pd.concat(
            [
                basic_info,
                pd.DataFrame(
                    {
                        "departement": dept_label,
                        "departement_id": dept_id,
                        "resume_activite": safe_get(chunk_df, "activity", "").fillna("")
                        + " "
                        + safe_get(chunk_df, "activityLight", "").fillna(""),
                        "raison_sociale": safe_get(chunk_df, "socialName", "").fillna(""),
                        "raison_sociale_keyword": safe_get(chunk_df, "internalName", "").fillna(""),
                        "last_modified": safe_get(chunk_df, "updatedAt", "").fillna(""),
                        "processedAt": safe_get(chunk_df, "createdAt", "").fillna(""),
                        "updatedAt": safe_get(chunk_df, "updatedAt", "").fillna(""),
                        "address": safe_get(chunk_df, "address", "").fillna(""),
                        "cp": safe_get(chunk_df, "cp", "").fillna(""),
                        "ville": safe_get(chunk_df, "ville", "").fillna(""),
                        "naf_code": naf_code,
                        "naf_label": naf_label,
                        "juridic_form": juridic_form,
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["01_company_basic_info"].append(basic_info)

        financial = base_index.copy()
        financial = pd.concat(
            [
                financial,
                pd.DataFrame(
                    {
                        "caConsolide": safe_get(chunk_df, "caConsolide", "").fillna(""),
                        "caGroupe": safe_get(chunk_df, "caGroupe", "").fillna(""),
                        "caBilan": safe_get(chunk_df, "caBilan", "").fillna(""),
                        "resultatExploitation": safe_get(chunk_df, "resultatExploitation", "").fillna(""),
                        "resultatNet": safe_get(chunk_df, "resultatNet", "").fillna(""),
                        "fondsPropres": safe_get(chunk_df, "fondsPropres", "").fillna(""),
                        "dateConsolide": safe_get(chunk_df, "dateCloture", "").fillna(""),
                        "trancheCaBilan": safe_get(chunk_df, "trancheCaBilan", "").fillna(""),
                        "trancheCaConsolide": safe_get(chunk_df, "trancheCaConsolide", "").fillna(""),
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["02_financial_data"].append(financial)

        workforce = base_index.copy()
        workforce = pd.concat(
            [
                workforce,
                pd.DataFrame(
                    {
                        "effectif": safe_get(chunk_df, "effectif", "").fillna(""),
                        "effectifConsolide": safe_get(chunk_df, "effectifConsolide", "").fillna(""),
                        "effectifGroupe": safe_get(chunk_df, "effectifGroupe", "").fillna(""),
                        "trancheEffectifConsolide": safe_get(chunk_df, "trancheEffectifConsolide", "").fillna(""),
                        "trancheEffectifPrecis": safe_get(chunk_df, "trancheEffectifPrecis", "").fillna(""),
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["03_workforce_data"].append(workforce)

        structure = base_index.copy()
        structure = pd.concat(
            [
                structure,
                pd.DataFrame(
                    {
                        "nbEtabSecondaire": safe_get(chunk_df, "nbEtabSecondaire", "").fillna(""),
                        "nbMarques": safe_get(chunk_df, "nbMarques", "").fillna(""),
                        "hasGroupOwner": safe_get(chunk_df, "hasGroupOwner", False).astype(bool),
                        "groupOwnerSiren": safe_get(chunk_df, "groupOwnerSiren", "").fillna(""),
                        "groupOwnerSocialName": safe_get(chunk_df, "groupOwnerSocialName", "").fillna(""),
                        "hasEtabSecondaire": safe_get(chunk_df, "hasEtabSecondaire", False).astype(bool),
                        "nbActionnaires": safe_get(chunk_df, "nbActionnaires", "").fillna(""),
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["04_company_structure"].append(structure)

        flags = base_index.copy()
        flags = pd.concat(
            [
                flags,
                pd.DataFrame(
                    {
                        "startup": chunk_df.get("startup", pd.Series([False] * len(chunk_df))).astype(bool),
                        "radiee": safe_get(chunk_df, "radiate", False).astype(bool),
                        "entreprise_b2b": safe_get(chunk_df, "bToB", False).astype(bool),
                        "entreprise_b2c": safe_get(chunk_df, "bToC", False).astype(bool),
                        "fintech": safe_get(chunk_df, "entreprise_fintech", False).astype(bool),
                        "cac40": safe_get(chunk_df, "cac40", False).astype(bool),
                        "entreprise_familiale": safe_get(chunk_df, "entreprise_familiale", False).astype(bool),
                        "entreprise_biotech_medtech": safe_get(
                            chunk_df, "entreprise_biotech_medtech", False
                        ).astype(bool),
                        "hasMarques": safe_get(chunk_df, "hasMarques", False).astype(bool),
                        "hasESV1Contacts": safe_get(chunk_df, "hasESV1Contacts", False).astype(bool),
                        "hasBrevets": safe_get(chunk_df, "hasBrevets", False).astype(bool),
                        "hasBodacc": safe_get(chunk_df, "hasBodacc", False).astype(bool),
                        "site_ecommerce": safe_get(chunk_df, "site_ecommerce", False).astype(bool),
                        "risk": safe_get(chunk_df, "risk", False).astype(bool),
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["05_classification_flags"].append(flags)

        contacts = base_index.copy()
        contacts = pd.concat(
            [
                contacts,
                pd.DataFrame(
                    {
                        "nbContacts": safe_get(chunk_df, "nbContacts", 0).fillna(0),
                        "emailContact": safe_get(chunk_df, "emailContact", "").fillna(""),
                        "telephoneNumber": safe_get(chunk_df, "telephoneNumber", "").fillna(""),
                        "webSite": safe_get(chunk_df, "webSite", "").fillna(""),
                        "urlLinkedin": safe_get(chunk_df, "urlLinkedin", "").fillna(""),
                        "urlFacebook": safe_get(chunk_df, "urlFacebook", "").fillna(""),
                        "urlTwitter": safe_get(chunk_df, "urlTwitter", "").fillna(""),
                    }
                ),
            ],
            axis=1,
        )
        self.dataframes["06_contact_metrics"].append(contacts)

        kpi_records: List[Dict[str, Any]] = []

        def extract_kpi_from_record(row, kpi_data):
            if pd.notna(kpi_data) and isinstance(kpi_data, dict):
                base_kpi = {
                    "company_name": str(row.get("socialName", "")) if pd.notna(row.get("socialName")) else "",
                    "siren": str(row.get("siren", "")) if pd.notna(row.get("siren")) else "",
                    "siret": format_siret(row.get("siret", "")) if pd.notna(row.get("siret")) else "",
                }
                for year, year_kpis in kpi_data.items():
                    if isinstance(year_kpis, dict):
                        kpi_row = base_kpi.copy()
                        kpi_row["year"] = str(year)
                        kpi_row.update(year_kpis)
                        kpi_records.append(kpi_row)

        for _, row in chunk_df.iterrows():
            kpi_data = None
            social_name = row.get("socialName", "")
            siren_val = row.get("siren", "")
            siret_val = row.get("siret", "")
            
            # Try multiple ways to access KPI data
            # 1. Top-level "kpi" column
            if "kpi" in chunk_df.columns:
                kpi_data = row.get("kpi")
                if pd.notna(kpi_data) and isinstance(kpi_data, dict):
                    extract_kpi_from_record(row, kpi_data)
                    continue
            
            # 2. Flattened column name "computed.kpi" (after pd.json_normalize)
            if "computed.kpi" in chunk_df.columns:
                kpi_data = row.get("computed.kpi")
                if pd.notna(kpi_data) and isinstance(kpi_data, dict):
                    extract_kpi_from_record(row, kpi_data)
                    continue
            
            # 3. Nested in "computed" column (as dict or object)
            if "computed" in chunk_df.columns:
                computed = row.get("computed")
                if pd.notna(computed):
                    if isinstance(computed, dict):
                        kpi_data = computed.get("kpi")
                        if kpi_data and isinstance(kpi_data, dict):
                            extract_kpi_from_record(row, kpi_data)
                            continue
                    # Handle case where computed is a string that needs parsing
                    elif isinstance(computed, str) and computed:
                        try:
                            import json
                            computed_dict = json.loads(computed)
                            if isinstance(computed_dict, dict):
                                kpi_data = computed_dict.get("kpi")
                                if kpi_data and isinstance(kpi_data, dict):
                                    extract_kpi_from_record(row, kpi_data)
                                    continue
                        except (json.JSONDecodeError, TypeError):
                            pass
            
            # 4. Flattened column name "v1legacy.kpi" (after pd.json_normalize)
            if "v1legacy.kpi" in chunk_df.columns:
                kpi_data = row.get("v1legacy.kpi")
                if pd.notna(kpi_data) and isinstance(kpi_data, dict):
                    extract_kpi_from_record(row, kpi_data)
                    continue
            
            # 5. Nested in "v1legacy" column (as dict or object)
            if "v1legacy" in chunk_df.columns:
                v1legacy = row.get("v1legacy")
                if pd.notna(v1legacy):
                    if isinstance(v1legacy, dict):
                        kpi_data = v1legacy.get("kpi")
                        if kpi_data and isinstance(kpi_data, dict):
                            extract_kpi_from_record(row, kpi_data)
                            continue
                    # Handle case where v1legacy is a string that needs parsing
                    elif isinstance(v1legacy, str) and v1legacy:
                        try:
                            import json
                            v1legacy_dict = json.loads(v1legacy)
                            if isinstance(v1legacy_dict, dict):
                                kpi_data = v1legacy_dict.get("kpi")
                                if kpi_data and isinstance(kpi_data, dict):
                                    extract_kpi_from_record(row, kpi_data)
                                    continue
                        except (json.JSONDecodeError, TypeError):
                            pass

        if kpi_records:
            kpi_df = pd.DataFrame(kpi_records)
            self.dataframes["07_kpi_data"].append(kpi_df)

        if not chunk_df.empty:
            records = chunk_df.to_dict("records")
            articles_records: List[Dict[str, Any]] = []
            signals_records: List[Dict[str, Any]] = []

            def extract_articles_from_record(record, articles_data):
                if not articles_data:
                    return
                articles_list = articles_data if isinstance(articles_data, list) else [articles_data]
                for article in articles_list:
                    if article and (isinstance(article, dict) or isinstance(article, list)):
                        if isinstance(article, dict):
                            article_with_company = article.copy()
                        else:
                            article_with_company = {}
                        if "companies" not in article_with_company:
                            article_with_company["companies"] = []
                        company_info = {
                            "label": record.get("socialName", ""),
                            "siren": record.get("siren", ""),
                            "siret": record.get("siret", ""),
                        }
                        if company_info not in article_with_company["companies"]:
                            article_with_company["companies"].append(company_info)
                        articles_records.append(article_with_company)

            for record in records:
                if "article" in record and record["article"]:
                    extract_articles_from_record(record, record["article"])
                if "articles" in record and record["articles"]:
                    extract_articles_from_record(record, record["articles"])
                if "computed" in record and isinstance(record.get("computed"), dict):
                    computed = record["computed"]
                    if "article" in computed and computed["article"]:
                        extract_articles_from_record(record, computed["article"])
                    if "articles" in computed and computed["articles"]:
                        extract_articles_from_record(record, computed["articles"])
                if "v1legacy" in record and isinstance(record.get("v1legacy"), dict):
                    v1legacy = record["v1legacy"]
                    if "article" in v1legacy and v1legacy["article"]:
                        extract_articles_from_record(record, v1legacy["article"])
                    if "articles" in v1legacy and v1legacy["articles"]:
                        extract_articles_from_record(record, v1legacy["articles"])

                if "signals" in record and record["signals"]:
                    signals_list = record["signals"] if isinstance(record["signals"], list) else [record["signals"]]
                    for signal in signals_list:
                        if signal:
                            signals_records.append(signal if isinstance(signal, dict) else {})
                elif "projects" in record and record["projects"]:
                    projects_list = record["projects"] if isinstance(record["projects"], list) else [record["projects"]]
                    for project in projects_list:
                        if project:
                            signals_records.append(project if isinstance(project, dict) else {})

            if articles_records:
                try:
                    articles_df = pd.DataFrame(articles_records)
                    self.articles_extractor.extract_chunk(articles_df)
                except Exception as exc:  # pragma: no cover - log only
                    print(f"Warning: Failed to extract articles: {exc}")

            if signals_records:
                try:
                    signals_df = pd.DataFrame(signals_records)
                    self.signals_extractor.extract_chunk(signals_df)
                except Exception as exc:  # pragma: no cover - log only
                    print(f"Warning: Failed to extract signals: {exc}")

    def get_datasets(self) -> Dict[str, pd.DataFrame]:
        """Return all extracted datasets as DataFrames."""
        result = {}
        for name, df_list in self.dataframes.items():
            if df_list:
                result[name] = pd.concat(df_list, ignore_index=True)
            else:
                result[name] = pd.DataFrame()

        articles_datasets = self.articles_extractor.get_datasets()
        signals_datasets = self.signals_extractor.get_datasets()

        result.update(articles_datasets)
        result.update(signals_datasets)

        return result

