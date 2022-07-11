#!/bin/sh

# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$ID_RSA_PASSPHRASE" \
--output ansible/id_rsa ansible/id_rsa.gpg
