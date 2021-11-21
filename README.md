# coingecko

Skripta ko išče nove coine na strani coingecko. Ko najde novega, telegram-bot pošlje v telegram grupo msg z imenom in linkom novega coina, medtem ga shrani v json file. 
skripta ima še funkcijo da lahko telegram-botu napišem ime coina, ki sem ga kupil. Skripta gre v json file in spremeni bought-attribute tega coina v True iz False. 
Istočasno s preverjanjem coingecko strani, preverja tudi kupljene coine, kdaj pridejo na coinmarketcap. Če kateri od kupljenih prispe na CMC, 
telegram-bot pošlje sporočilo z imenom in linkom coina, da je prispel na CMC. V tistem trenutku je pričakovano da se bo v naslednjih par urah coin prodal. 
Zato skripta spremeni bought-attribute v "sold". In ne preverja več tega coina.
