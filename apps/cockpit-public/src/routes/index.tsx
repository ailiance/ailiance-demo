import { seo } from '@/lib/seo';
import { createFileRoute } from '@tanstack/react-router';

export const Route = createFileRoute('/')({
  head: () =>
    seo({
      title: "Ailiance — Modèles d'IA ouverts adaptés à vos données métier",
      description:
        "Ailiance adapte des modèles d'IA ouverts — génératifs ou non — à votre métier. Nous structurons et entraînons vos données pour améliorer vos process. Méthode en 6 étapes, données 100 % on-premise, de l'audit initial à la mise en production.",
      path: '/',
    }),
});
