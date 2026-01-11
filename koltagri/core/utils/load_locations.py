# seu_app/management/commands/load_brazil_locations.py

import requests
from django.core.management.base import BaseCommand
from django.db import transaction

from koltagri.core.models import Country, State, City


class Command(BaseCommand):
    help = "Popula o banco com estados e cidades do Brasil (IBGE)"

    IBGE_STATES_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
    IBGE_CITIES_URL = "https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("📌 Iniciando carga de estados e cidades do Brasil...")

        # País
        brazil, _ = Country.objects.get_or_create(
            abbreviation="BR",
            defaults={"name": "Brasil"}
        )

        states_response = requests.get(self.IBGE_STATES_URL)
        states_response.raise_for_status()
        states_data = states_response.json()

        for state_data in states_data:
            state, created = State.objects.get_or_create(
                name=state_data["nome"],
                country=brazil
            )

            if created:
                self.stdout.write(f"✔ Estado criado: {state.name}")
            else:
                self.stdout.write(f"⏭ Estado já existe: {state.name}")

            cities_url = self.IBGE_CITIES_URL.format(uf=state_data["sigla"])
            cities_response = requests.get(cities_url)
            cities_response.raise_for_status()
            cities_data = cities_response.json()

            cities_to_create = []
            for city_data in cities_data:
                if not City.objects.filter(
                    name=city_data["nome"],
                    state=state
                ).exists():
                    cities_to_create.append(
                        City(
                            name=city_data["nome"],
                            state=state
                        )
                    )

            City.objects.bulk_create(cities_to_create)
            self.stdout.write(
                f"   └── {len(cities_to_create)} cidades adicionadas"
            )

        self.stdout.write(self.style.SUCCESS("✅ Carga finalizada com sucesso!"))
