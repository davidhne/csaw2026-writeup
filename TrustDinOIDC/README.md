# TrustDinOIDC

## Oppgaven

En OIDC-portal (`trustdinoidc-portal`) som logger inn brukere via en ekstern
identity provider (`strataid.example.com`, kalt "Strata"). Portalen tar imot
en `id_token` (en JWT) fra login-flyten og stoler på den for å avgjøre
brukerens identitet og rettigheter (`sub`, `scope`).

## Sårbarheten

JWT-en har en `x5c`-header — et innebygd X.509-sertifikat som (i teorien) skal
bevise at signaturen kommer fra en betrodd utsteder. Problemet er at
verifiseringen ser ut til å stole på **sertifikatet som allerede ligger inni
selve token-en**, i stedet for å sjekke det mot en fastpinnet/kjent
public key for `strataid.example.com`. Navnet på flagget treffer spikeren på
hodet: Strata "hoppet over pin-en" (skippet public-key-pinning).

Det betyr at hvem som helst kan:
1. Generere sitt eget RSA-nøkkelpar.
2. Lage et selvsignert sertifikat med `CN=strataid.example.com` (later som om
   det er utsteders sertifikat).
3. Signere en helt egen JWT-payload med sin egen private nøkkel, og legge det
   selvsignerte sertifikatet i `x5c`-headeren.
4. Sende denne forfalskede token-en til portalens callback-endepunkt — siden
   serveren bare sjekker signaturen mot sertifikatet i tokenen selv (som jo
   stemmer, siden vi signerte med samme nøkkelpar), blir den godtatt som ekte.

## `forge.py` — exploiten

Scriptet:
- Genererer en RSA-nøkkel og et selvsignert sertifikat for
  `strataid.example.com`.
- Bygger en JWT-header med `x5c` satt til dette sertifikatet.
- Bygger en payload med `"sub": "admin"` og utvidet scope
  (`freeosaurus:redeem flagosaurus:redeem`) i stedet for den vanlige
  gjeste-scopen.
- Signerer token-en med sin egen private nøkkel (`RS256`).
- Skriver ut en `poc.html` som auto-submitter denne forfalskede token-en som
  `id_token` til portalens `/oauth/callback`-endepunkt.

```bash
python3 forge.py
# åpne den genererte poc.html i nettleser, eller post token direkte til callback
```

Resultatet er en innlogget "admin"-sesjon med tilgang til
`flagosaurus:redeem`-scopet, som ga flagget.



**Flag:** `csaw{str4ta_sk1pped_th3_p1n}`
