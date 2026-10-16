import secrets
import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.db.models import F, Q, Value
from django.db.models.functions import Length, Lower, Now
from django.db.models.lookups import GreaterThanOrEqual, LessThanOrEqual
from django.utils import timezone


def nouveau_qr_code() -> str:
    return secrets.token_hex(32)


class JetonQR(models.Func):
    template = "encode(gen_random_bytes(32), 'hex')"
    output_field = models.CharField()


class IdentifiantUUID(models.Func):
    template = "gen_random_uuid()"
    output_field = models.UUIDField()


def longueur(champ: str, minimum: int, maximum: int):
    taille = Length(champ)
    return GreaterThanOrEqual(taille, minimum) & LessThanOrEqual(taille, maximum)


def au_plus(champ: str, maximum: int):
    return LessThanOrEqual(Length(champ), maximum)


EMAIL_REGEX = r"^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$"
VISUEL_REGEX = r"^https?://[^[:space:]]+$"


class StatutCompte(models.TextChoices):
    ACTIF = "actif", "actif"
    INACTIF = "inactif", "inactif"


class StatutInvitation(models.TextChoices):
    BROUILLON = "brouillon", "brouillon"
    PUBLIE = "publié", "publié"
    CLOS = "clos", "clos"


class CanalMessage(models.TextChoices):
    EMAIL = "email", "email"
    WHATSAPP = "whatsapp", "whatsapp"


class StatutRSVP(models.TextChoices):
    EN_ATTENTE = "en_attente", "en_attente"
    ACCEPTE = "accepté", "accepté"
    REFUSE = "refusé", "refusé"


class ResultatPresence(models.TextChoices):
    VALIDE = "validé", "validé"
    REFUSE = "refusé", "refusé"
    DEJA_SCANNE = "déjà_scanné", "déjà_scanné"


class MethodePresence(models.TextChoices):
    SCAN_QR = "scan_qr", "scan_qr"


class TypeAcces(models.TextChoices):
    CHECK_IN = "check_in_uniquement", "check_in_uniquement"
    GESTION_INVITES = "gestion_invites", "gestion_invites"
    GESTION_COMPLETE = "gestion_complete", "gestion_complete"


class StatutEnvoi(models.TextChoices):
    ENVOYE = "envoyé", "envoyé"
    LIVRE = "livré", "livré"
    ECHOUE = "échoué", "échoué"


class TypeChamp(models.TextChoices):
    TEXTE = "texte", "texte"
    CHOIX = "choix", "choix"
    NOMBRE = "nombre", "nombre"


class CompteAvecMotDePasse(models.Model):
    """Champs communs. Le mot de passe n'est jamais conservé en clair."""

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        db_default=IdentifiantUUID(),
    )
    nom = models.CharField(max_length=200)
    email = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=20)
    mot_de_passe_hash = models.CharField(max_length=255, editable=False)
    statut = models.CharField(max_length=20, choices=StatutCompte.choices)
    date_creation = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        abstract = True

    def definir_mot_de_passe(self, mot_de_passe_en_clair: str) -> None:
        if not mot_de_passe_en_clair:
            raise ValueError("mot de passe vide")
        self.mot_de_passe_hash = make_password(mot_de_passe_en_clair)

    def verifier_mot_de_passe(self, mot_de_passe_en_clair: str) -> bool:
        if not self.mot_de_passe_hash:
            return False
        return check_password(mot_de_passe_en_clair, self.mot_de_passe_hash)

    def __str__(self) -> str:
        return self.nom


class Organisateur(CompteAvecMotDePasse):
    tenant_ref = models.UUIDField(
        null=True,
        blank=True,
        db_comment="Référence externe sans clé étrangère",
    )

    class Meta:
        db_table = "organisateurs"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=[StatutCompte.ACTIF, StatutCompte.INACTIF]),
                name="ck_organisateurs_statut",
            ),
            models.CheckConstraint(
                condition=longueur("nom", 1, 200),
                name="ck_organisateurs_nom",
            ),
            models.CheckConstraint(
                condition=Q(email__regex=EMAIL_REGEX),
                name="ck_organisateurs_email",
            ),
            models.CheckConstraint(
                condition=longueur("telephone", 8, 20),
                name="ck_organisateurs_telephone",
            ),
            models.CheckConstraint(
                condition=GreaterThanOrEqual(Length("mot_de_passe_hash"), 1),
                name="ck_organisateurs_mot_de_passe_hash",
            ),
            models.UniqueConstraint(
                Lower("email"),
                name="uq_organisateurs_email_lower",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant_ref"], name="ix_organisateurs_tenant_ref"),
        ]


class MiddleUser(CompteAvecMotDePasse):
    organisateur = models.ForeignKey(
        Organisateur,
        on_delete=models.RESTRICT,
        related_name="middle_users",
        db_index=False,
    )

    class Meta:
        db_table = "middle_users"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=[StatutCompte.ACTIF, StatutCompte.INACTIF]),
                name="ck_middle_users_statut",
            ),
            models.CheckConstraint(condition=longueur("nom", 1, 200), name="ck_middle_users_nom"),
            models.CheckConstraint(
                condition=Q(email__regex=EMAIL_REGEX),
                name="ck_middle_users_email",
            ),
            models.CheckConstraint(
                condition=longueur("telephone", 8, 20),
                name="ck_middle_users_telephone",
            ),
            models.CheckConstraint(
                condition=GreaterThanOrEqual(Length("mot_de_passe_hash"), 1),
                name="ck_middle_users_mot_de_passe_hash",
            ),
            models.UniqueConstraint(Lower("email"), name="uq_middle_users_email_lower"),
        ]
        indexes = [
            models.Index(fields=["organisateur"], name="ix_middle_users_organisateur"),
        ]


class CategorieInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    nom = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    icone_couleur = models.CharField(max_length=7)

    class Meta:
        db_table = "categories_invitation"
        constraints = [
            models.CheckConstraint(
                condition=longueur("nom", 1, 200),
                name="ck_categories_invitation_nom",
            ),
            models.CheckConstraint(
                condition=Q(description__isnull=True) | au_plus("description", 5000),
                name="ck_categories_invitation_description",
            ),
            models.CheckConstraint(
                condition=Q(icone_couleur__regex=r"^#[0-9A-Fa-f]{6}$"),
                name="ck_categories_invitation_icone",
            ),
        ]

    def __str__(self) -> str:
        return self.nom


class TemplateInvitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    categorie = models.ForeignKey(
        CategorieInvitation,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="templates",
        db_index=False,
    )
    organisateur = models.ForeignKey(
        Organisateur,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="templates",
        db_index=False,
        db_comment="Null = modèle fourni par la plateforme",
    )
    nom = models.CharField(max_length=200)
    contenu = models.TextField()
    visuel_url = models.CharField(max_length=500, null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "templates_invitation"
        constraints = [
            models.CheckConstraint(
                condition=longueur("nom", 1, 200),
                name="ck_templates_invitation_nom",
            ),
            models.CheckConstraint(
                condition=longueur("contenu", 1, 10000),
                name="ck_templates_invitation_contenu",
            ),
            models.CheckConstraint(
                condition=Q(visuel_url__isnull=True) | Q(visuel_url__regex=VISUEL_REGEX),
                name="ck_templates_invitation_visuel",
            ),
        ]
        indexes = [
            models.Index(fields=["categorie"], name="ix_templates_categorie"),
            models.Index(fields=["organisateur"], name="ix_templates_organisateur"),
        ]

    def __str__(self) -> str:
        return self.nom


class Invitation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    organisateur = models.ForeignKey(
        Organisateur,
        on_delete=models.RESTRICT,
        related_name="invitations",
        db_index=False,
    )
    categorie = models.ForeignKey(
        CategorieInvitation,
        on_delete=models.RESTRICT,
        related_name="invitations",
        db_index=False,
    )
    template = models.ForeignKey(
        TemplateInvitation,
        null=True,
        blank=True,
        on_delete=models.RESTRICT,
        related_name="invitations",
        db_index=False,
    )
    titre = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    lieu = models.CharField(max_length=300, null=True, blank=True)
    date_evenement = models.DateTimeField(null=True, blank=True)
    date_limite_rsvp = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=StatutInvitation.choices)
    visuel_url = models.CharField(max_length=500, null=True, blank=True)
    date_creation = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "invitations"
        constraints = [
            models.CheckConstraint(
                condition=Q(statut__in=StatutInvitation.values),
                name="ck_invitations_statut",
            ),
            models.CheckConstraint(condition=longueur("titre", 1, 200), name="ck_invitations_titre"),
            models.CheckConstraint(
                condition=Q(description__isnull=True) | au_plus("description", 5000),
                name="ck_invitations_description",
            ),
            models.CheckConstraint(
                condition=Q(lieu__isnull=True) | longueur("lieu", 1, 300),
                name="ck_invitations_lieu",
            ),
            models.CheckConstraint(
                condition=Q(visuel_url__isnull=True) | Q(visuel_url__regex=VISUEL_REGEX),
                name="ck_invitations_visuel",
            ),
            models.CheckConstraint(
                condition=Q(date_evenement__isnull=True)
                | Q(date_limite_rsvp__isnull=True)
                | Q(date_limite_rsvp__lte=F("date_evenement")),
                name="ck_invitations_dates_ordre",
            ),
            models.CheckConstraint(
                condition=Q(statut=StatutInvitation.BROUILLON)
                | (
                    Q(lieu__isnull=False)
                    & Q(date_evenement__isnull=False)
                    & Q(date_limite_rsvp__isnull=False)
                ),
                name="ck_invitations_publication",
            ),
        ]
        indexes = [
            models.Index(fields=["organisateur"], name="ix_invitations_organisateur"),
            models.Index(fields=["categorie"], name="ix_invitations_categorie_id"),
            models.Index(fields=["template"], name="ix_invitations_template_id"),
            models.Index(fields=["statut"], name="ix_invitations_statut"),
        ]

    def __str__(self) -> str:
        return self.titre


class Invite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.RESTRICT,
        related_name="invites",
        db_index=False,
    )
    nom = models.CharField(max_length=200)
    email = models.EmailField(max_length=254, null=True, blank=True)
    telephone = models.CharField(max_length=20, null=True, blank=True)
    canal_prefere = models.CharField(max_length=20, choices=CanalMessage.choices)
    qr_code = models.CharField(
        max_length=64,
        unique=True,
        default=nouveau_qr_code,
        editable=False,
        db_default=JetonQR(),
        db_comment="Jeton opaque, sans donnée personnelle",
    )
    statut_rsvp = models.CharField(
        max_length=20,
        choices=StatutRSVP.choices,
        default=StatutRSVP.EN_ATTENTE,
        db_default=Value("en_attente"),
    )
    date_reponse = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "invites"
        constraints = [
            models.UniqueConstraint(fields=["id", "invitation"], name="uq_invites_id_invitation"),
            models.CheckConstraint(
                condition=Q(canal_prefere__in=CanalMessage.values),
                name="ck_invites_canal_prefere",
            ),
            models.CheckConstraint(
                condition=Q(statut_rsvp__in=StatutRSVP.values),
                name="ck_invites_statut_rsvp",
            ),
            models.CheckConstraint(condition=longueur("nom", 1, 200), name="ck_invites_nom"),
            models.CheckConstraint(
                condition=Q(email__isnull=True) | Q(email__regex=EMAIL_REGEX),
                name="ck_invites_email",
            ),
            models.CheckConstraint(
                condition=Q(telephone__isnull=True) | longueur("telephone", 8, 20),
                name="ck_invites_telephone",
            ),
            models.CheckConstraint(
                condition=(Q(canal_prefere=CanalMessage.EMAIL) & Q(email__isnull=False))
                | (Q(canal_prefere=CanalMessage.WHATSAPP) & Q(telephone__isnull=False)),
                name="ck_invites_contact_canal",
            ),
            models.CheckConstraint(
                condition=(Q(statut_rsvp=StatutRSVP.EN_ATTENTE) & Q(date_reponse__isnull=True))
                | (~Q(statut_rsvp=StatutRSVP.EN_ATTENTE) & Q(date_reponse__isnull=False)),
                name="ck_invites_date_reponse",
            ),
            models.CheckConstraint(
                condition=Q(qr_code__regex=r"^[0-9a-f]{64}$"),
                name="ck_invites_qr_code",
            ),
            models.CheckConstraint(
                condition=~Q(qr_code=F("email")) & ~Q(qr_code=F("telephone")),
                name="ck_invites_qr_sans_contact",
            ),
        ]
        indexes = [
            models.Index(fields=["invitation"], name="ix_invites_invitation_id"),
        ]

    def __str__(self) -> str:
        return self.nom


class Presence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    invite = models.ForeignKey(
        Invite,
        on_delete=models.RESTRICT,
        related_name="presences",
        db_index=False,
    )
    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.RESTRICT,
        related_name="presences",
        db_index=False,
    )
    coherence_invite = models.ForeignObject(
        Invite,
        on_delete=models.RESTRICT,
        from_fields=["invite_id", "invitation_id"],
        to_fields=["id", "invitation_id"],
        related_name="+",
    )
    middle_user = models.ForeignKey(
        MiddleUser,
        on_delete=models.RESTRICT,
        related_name="presences",
        db_index=False,
    )
    horodatage = models.DateTimeField(default=timezone.now, db_default=Now())
    resultat = models.CharField(max_length=20, choices=ResultatPresence.choices)
    methode = models.CharField(max_length=20, choices=MethodePresence.choices)

    class Meta:
        db_table = "presences"
        constraints = [
            models.CheckConstraint(
                condition=Q(resultat__in=ResultatPresence.values),
                name="ck_presences_resultat",
            ),
            models.CheckConstraint(
                condition=Q(methode__in=MethodePresence.values),
                name="ck_presences_methode",
            ),
            models.UniqueConstraint(
                fields=["invite"],
                condition=Q(resultat=ResultatPresence.VALIDE),
                name="uq_presences_une_validation",
            ),
        ]
        indexes = [
            models.Index(fields=["middle_user"], name="ix_presences_middle_user_id"),
            models.Index(fields=["invitation"], name="ix_presences_invitation_id"),
        ]


class AccesMiddleUser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    middle_user = models.ForeignKey(
        MiddleUser,
        on_delete=models.RESTRICT,
        related_name="acces",
        db_index=False,
    )
    invitation = models.ForeignKey(
        Invitation,
        on_delete=models.RESTRICT,
        related_name="acces",
        db_index=False,
    )
    type_acces = models.CharField(max_length=32, choices=TypeAcces.choices)
    date_attribution = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "acces_middle_users"
        constraints = [
            models.UniqueConstraint(
                fields=["middle_user", "invitation"],
                name="uq_acces_middle_users_paire",
            ),
            models.CheckConstraint(
                condition=Q(type_acces__in=TypeAcces.values),
                name="ck_acces_middle_users_type_acces",
            ),
        ]
        indexes = [
            models.Index(fields=["invitation"], name="ix_acces_invitation"),
        ]


class Envoi(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    invite = models.ForeignKey(Invite, on_delete=models.RESTRICT, related_name="envois")
    canal = models.CharField(max_length=20, choices=CanalMessage.choices)
    statut = models.CharField(max_length=20, choices=StatutEnvoi.choices)
    tentative_numero = models.PositiveIntegerField()
    date_envoi = models.DateTimeField(default=timezone.now, db_default=Now())

    class Meta:
        db_table = "envois"
        constraints = [
            models.UniqueConstraint(
                fields=["invite", "canal", "tentative_numero"],
                name="uq_envois_tentative",
            ),
            models.CheckConstraint(
                condition=Q(canal__in=CanalMessage.values),
                name="ck_envois_canal",
            ),
            models.CheckConstraint(
                condition=Q(statut__in=StatutEnvoi.values),
                name="ck_envois_statut",
            ),
            models.CheckConstraint(
                condition=Q(tentative_numero__gte=1),
                name="ck_envois_tentative_numero",
            ),
        ]


class Accompagnant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    invite = models.ForeignKey(
        Invite,
        on_delete=models.RESTRICT,
        related_name="accompagnants",
        db_index=False,
    )
    nom = models.CharField(max_length=200, null=True, blank=True)
    present = models.BooleanField(default=False, db_default=False)

    class Meta:
        db_table = "accompagnants"
        constraints = [
            models.CheckConstraint(
                condition=Q(nom__isnull=True) | longueur("nom", 1, 200),
                name="ck_accompagnants_nom",
            ),
        ]
        indexes = [
            models.Index(fields=["invite"], name="ix_accompagnants_invite_id"),
        ]


class ChampPersonnalise(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    categorie = models.ForeignKey(
        CategorieInvitation,
        on_delete=models.RESTRICT,
        related_name="champs",
    )
    libelle = models.CharField(max_length=200)
    type_champ = models.CharField(max_length=20, choices=TypeChamp.choices)
    obligatoire = models.BooleanField()

    class Meta:
        db_table = "champs_personnalises"
        constraints = [
            models.UniqueConstraint(
                fields=["categorie", "libelle"],
                name="uq_champs_personnalises_libelle",
            ),
            models.CheckConstraint(
                condition=Q(type_champ__in=TypeChamp.values),
                name="ck_champs_personnalises_type_champ",
            ),
            models.CheckConstraint(
                condition=longueur("libelle", 1, 200),
                name="ck_champs_personnalises_libelle",
            ),
        ]


class OptionChamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    champ = models.ForeignKey(
        ChampPersonnalise,
        on_delete=models.RESTRICT,
        related_name="options",
    )
    libelle = models.CharField(max_length=200)
    ordre = models.PositiveIntegerField()

    class Meta:
        db_table = "options_champ"
        constraints = [
            models.UniqueConstraint(fields=["champ", "libelle"], name="uq_options_champ_libelle"),
            models.UniqueConstraint(fields=["champ", "ordre"], name="uq_options_champ_ordre"),
            models.CheckConstraint(
                condition=longueur("libelle", 1, 200),
                name="ck_options_champ_libelle",
            ),
            models.CheckConstraint(condition=Q(ordre__gte=0), name="ck_options_champ_ordre"),
        ]


class ReponseChamp(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_default=IdentifiantUUID())
    champ = models.ForeignKey(
        ChampPersonnalise,
        on_delete=models.RESTRICT,
        related_name="reponses",
    )
    invite = models.ForeignKey(
        Invite,
        on_delete=models.RESTRICT,
        related_name="reponses",
        db_index=False,
    )
    valeur = models.TextField()

    class Meta:
        db_table = "reponses_champ"
        constraints = [
            models.UniqueConstraint(fields=["champ", "invite"], name="uq_reponses_champ_paire"),
            models.CheckConstraint(
                condition=au_plus("valeur", 2000),
                name="ck_reponses_champ_valeur",
            ),
        ]
        indexes = [
            models.Index(fields=["invite"], name="ix_reponses_champ_invite_id"),
        ]
