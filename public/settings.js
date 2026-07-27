// Language preference v2: migrate the earlier browser-language default to
// Chinese once. A user's later manual choice remains persistent.
if (!localStorage.getItem("itr-language-v2-migrated")) {
  localStorage.setItem("itr-lang", "zh");
  localStorage.setItem("itr-language-v2-migrated", "1");
}
