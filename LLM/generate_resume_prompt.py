import json

from schemas import ResumeCreate

def build_resume_prompt(profile_data: dict, job_description: str) -> str:
    return (
        "Vous êtes un professionnel des ressources humaines chargé de créer un CV personnalisé pour un candidat "
        "à partir de ses informations de profil et d'une description de poste spécifique. Votre objectif est de générer un CV "
        "qui présente de manière claire et convaincante les compétences, la formation, les expériences, les certifications et les projets "
        "du candidat en mettant en exergue uniquement les éléments qui correspondent aux exigences du poste. "
        "N’introduisez aucune donnée nouvelle et ne modifiez en aucun cas les informations personnelles du candidat.\n\n"
        
        f"Données du profil du candidat (ne pas modifier) :\n{json.dumps(profile_data, indent=2)}\n\n"
        f"Description du poste :\n{job_description}\n\n"
        
        "En utilisant les informations fournies, créez un CV en tenant compte des points suivants :\n"
        "- Réécrivez et réordonnez les sections du CV pour mieux coller aux exigences du poste.\n"
        "- Supprimez les compétences, expériences, certifications et projets qui ne répondent pas directement aux critères du poste.\n"
        "- Reformulez certaines phrases pour accentuer l’adéquation du candidat avec les besoins de l’entreprise.\n"
        "- Conservez et affichez exactement les informations personnelles du candidat (full_name, email, phone, address, linkedin, facebook, x) telles qu'elles sont fournies.\n"
        "- Organisez les expériences professionnelles et la formation en ordre chronologique décroissant (du plus récent au plus ancien).\n"
        "- Utilisez une formulation concise, orientée action et conforme aux standards d'un CV professionnel.\n"
        "- Toutes les dates doivent respecter le format 'YYYY-MM-DD'.\n"
        "- Pour les champs optionnels (address, linkedin, facebook, x, end_date, link) qui ne figurent pas dans le profil, affectez-leur la valeur null.\n\n"
        
        "Générez le CV strictement au format JSON respectant le schéma ResumeCreate suivant. Ne fournissez aucun texte ou explication additionnelle.\n\n"
        
        f"Schéma JSON requis : {ResumeCreate.model_json_schema()}\n\n"
        
        "Assurez-vous que :\n"
        "- Toutes les dates sont au format 'YYYY-MM-DD'.\n"
        "- Les expériences professionnelles et la formation sont triées en ordre chronologique décroissant.\n"
        "- Seules les informations présentes dans le profil sont utilisées, et celles qui ne correspondent pas aux besoins du poste sont omises.\n"
        "- Les champs optionnels manquants sont explicitement définis à null.\n"
        "- Le résultat est un JSON valide respectant exactement le schéma fourni.\n\n"
        
        "Ne fournissez que le JSON en sortie, sans aucun commentaire ni texte complémentaire."
    )
