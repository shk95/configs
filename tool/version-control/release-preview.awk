# Strict data engine; no system(), getline commands, eval or candidate execution.
# INV repository/release-preview-read-only
# INV repository/evidence-three-states
function refuse(code) { errors[code]=1 }
function id(s) { return s ~ /^[a-z0-9][a-z0-9-]*$/ }
function sha(s) { return s ~ /^[a-f0-9]+$/ && (length(s)==40 || length(s)==64) }
function path(s) { return s!="" && s!="-" && s!~/^\// && s!~/(^|\/)\.\.(\/|$)/ && s!~/[[:cntrl:]]/ }
function version(s, v,n,i) { n=split(s,v,"[.]"); if(n!=3) return 0; for(i=1;i<=3;i++) if(v[i]!~/^(0|[1-9][0-9]*)$/) return 0; return 1 }
function quote(s) { gsub(/\\/,"\\\\",s); gsub(/"/,"\\\"",s); gsub(/\t/,"\\t",s); gsub(/\r/,"\\r",s); gsub(/\n/,"\\n",s); return "\"" s "\"" }
function keys(a, result, k,n,i,j,t) {
  n=0; for(k in a) result[++n]=k
  for(i=2;i<=n;i++) { t=result[i]; j=i-1; while(j>0 && result[j]>t) { result[j+1]=result[j]; j-- } result[j+1]=t }
  return n
}
function list(s, a, n,i,seen) {
  if(s=="-") return 0
  n=split(s,a,",")
  for(i=1;i<=n;i++) { if(!id(a[i]) || seen[a[i]]++) return -1 }
  return n
}
function require_check(check, visiting, d,n,i) {
  if(!check_domain[check]) { refuse("unknown-check"); return }
  if(visiting[check]) { refuse("dependency-cycle"); return }
  if(selected[check]) return
  visiting[check]=1; n=list(check_dependencies[check],d)
  if(n<0) refuse("invalid-dependencies")
  for(i=1;i<=n;i++) require_check(d[i],visiting)
  delete visiting[check]; selected[check]=1
}
function add_reason(check, reason, kind, seen,d,n,i) {
  if(seen[check]) return
  seen[check]=1; selection_reasons[check,kind,reason]=1
  if(kind=="promotion-delta")reasons[check,reason]=1
  n=list(check_dependencies[check],d)
  for(i=1;i<=n;i++) add_reason(d[i],reason,kind,seen)
}
function select_path(p, reason, m,n,cs,i,hit,visiting,seen) {
  hit=0
  for(m=1;m<=map_count;m++) {
    if((map_match[m]=="exact" && p==map_path[m]) || (map_match[m]=="prefix" && index(p,map_path[m])==1)) {
      hit=1; n=list(map_checks[m],cs)
      for(i=1;i<=n;i++) { require_check(cs[i],visiting); add_reason(cs[i],reason,"promotion-delta",seen) }
    }
  }
  if(!hit) refuse("mapping-review-needed")
}
function add_one(s, result,i,d,carry) {
  result=""; carry=1
  for(i=length(s);i>0;i--) { d=substr(s,i,1)+carry; if(d==10)d=0; else carry=0; result=d result }
  return (carry ? "1" : "") result
}
function increment(v, impact, p) {
  split(v,p,"[.]")
  if(impact==3) return add_one(p[1]) ".0.0"
  if(impact==2) return p[1] "." add_one(p[2]) ".0"
  return p[1] "." p[2] "." add_one(p[3])
}
BEGIN { impacts["none"]=0; impacts["patch"]=1; impacts["minor"]=2; impacts["major"]=3; names[0]="none"; names[1]="patch"; names[2]="minor"; names[3]="major" }
FNR==1 && FILENAME!=ARGV[4] { if($1!="format" || $2!="1" || NF!=2) refuse("invalid-replay-format"); next }
FILENAME!=ARGV[4] && /[\001-\010\013-\037\177]/ { refuse("invalid-control-character") }
FILENAME==ARGV[1] {
  if($1=="check") {
    if(NF!=7 || !id($2) || check_domain[$2] || $3!~/^(unixlike|windows|repository)$/ || $4!~/^(evaluation|build|native-runtime|fixtures|policy-checks|review)$/ || $5!~/^(required|advisory)$/ || $7=="") { refuse("invalid-check-definition"); next }
    check_domain[$2]=$3; check_lane[$2]=$4; check_requirement[$2]=$5; check_dependencies[$2]=$6; check_tool[$2]=$7
  } else if($1=="map") {
    if(NF!=4 || $2!~/^(exact|prefix)$/ || !path($3)) { refuse("invalid-map-definition"); next }
    if(map_seen[$2,$3,$4]++) refuse("duplicate-map-definition")
    map_match[++map_count]=$2; map_path[map_count]=$3; map_checks[map_count]=$4
  } else refuse("unknown-rule-record")
  next
}
FILENAME==ARGV[2] {
  if($2=="common") refuse("unsupported-common")
  if($2!~/^(unixlike|windows)$/ || baseline_kind[$2]) { refuse("invalid-baseline-domain"); next }
  if($1=="semantic") {
    if(NF!=5 || !sha($5) || !version($3) || $4!=$2 "-v" $3) refuse("invalid-semantic-baseline")
  } else if($1=="bootstrap") {
    if(NF!=5 || !sha($3) || !sha($4) || !path($5)) refuse("invalid-bootstrap-baseline")
  } else refuse("unknown-baseline-record")
  baseline_kind[$2]=$1; next
}
FILENAME==ARGV[3] {
  if($1=="evidence") {
    if(NF!=9 || !id($2) || evidence_seen[$2]++) { refuse("invalid-evidence-record"); next }
    evidence_candidate[$2]=$3; evidence_master[$2]=$4; evidence_tree[$2]=$5; evidence_rules[$2]=$6; evidence_tool[$2]=$7; evidence_state[$2]=$8; evidence_reference[$2]=$9
    if(!sha($3)||!sha($4)||!sha($5)||!sha($6)||$7==""||$8!~/^(verified|failed|unverified)$/||$9=="") refuse("invalid-evidence-record")
  } else if($1=="defect") {
    if(NF!=3 || !id($2) || $3=="") refuse("invalid-defect-record")
    if(defects[$2]) refuse("duplicate-defect-record")
    defects[$2]=$3
  } else refuse("unknown-evidence-record")
  next
}
FILENAME==ARGV[4] {
  if($1=="pending-source") { pending_source=$2+0
  } else if($1=="promotion") {
    promotion_path[$3]=$2; promotion_owner[$3]=$4
    if($4!="repository") affected[$4]=1
  } else if($1=="baseline") {
    domain_version[$2]=$3; domain_base[$2]=$4; domain_ref[$2]=$5; domain_record[$2]=$6
  } else if($1=="bootstrap") {
    if(NF!=4 || bootstrap_seen[$2,$3]++) refuse("invalid-bootstrap-record")
    bootstrap_value[$2,$3]=$4
  } else if($1=="delta") { domain_delta[$2]=1
  } else if($1=="history") {
    h=$2 SUBSEP $3; history_order[++history_count]=h; history_domain[h]=$2; history_sha[h]=$3; history_parent[h]=$4; history_digest[h]=$5
  } else if($1=="trailer") {
    h=$2 SUBSEP $3; key=$4
    if(NF!=5 || $5=="" || $5~/[[:cntrl:]]/ || trailer_count[h,key]++) refuse("invalid-release-trailer")
    if(key!~/^release-(format|domain|impact|contracts|compatibility|rationale|migration|reverts)$/) refuse("unknown-release-trailer")
    trailer[h,key]=$5
  } else if($1=="diff") {
    h=$2 SUBSEP $3; diff_count[h]++; diff_value[h,$9]=$4 "\t" $5 "\t" $6 "\t" $7
    diff_reverse[h,$9]=$5 "\t" $4 "\t" $7 "\t" $6
    diff_path[h,$9]=1
  } else if($1=="revert") { h=$2 SUBSEP $3; revert_target[h]=$4; revert_category[h]=$5
  } else if($1=="migration") { migration_exists[$2 SUBSEP $3]=$4
  } else refuse("unknown-derived-record")
  next
}
END {
  for(c in check_domain) {
    n=list(check_dependencies[c],values)
    if(n<0) refuse("invalid-dependencies")
    for(i=1;i<=n;i++) if(!check_domain[values[i]]) refuse("unknown-check")
  }
  # Validate cycles even for currently unselected definitions.
  for(c in check_domain) require_check(c,visit)
  for(c in selected) delete selected[c]
  for(m=1;m<=map_count;m++) {
    n=list(map_checks[m],values)
    if(n<1) refuse("invalid-map-checks")
    for(i=1;i<=n;i++) if(!check_domain[values[i]]) refuse("unknown-check")
  }
  for(p in promotion_path) select_path(p,p)
  for(d in affected) if(!baseline_kind[d]) refuse("missing-domain-baseline")
  for(d in baseline_kind) {
    if(baseline_kind[d]=="bootstrap") {
      if(bootstrap_value[d,"format"]!="1" || bootstrap_value[d,"domain"]!=d || bootstrap_value[d,"source"]!=candidate || bootstrap_value[d,"version"]!="1.0.0") refuse("bootstrap-record-mismatch")
      count=0; for(k in bootstrap_seen) { split(k,parts,SUBSEP); if(parts[1]==d) { count++; if(parts[2]!~/^(format|domain|source|version|contracts)$/) refuse("unknown-bootstrap-field") } }
      if(count!=5) refuse("invalid-bootstrap-record")
      n=list(bootstrap_value[d,"contracts"],values)
      if(n<1) refuse("invalid-bootstrap-contracts")
      for(i=1;i<=n;i++) { if(check_domain[values[i]]!=d) refuse("invalid-bootstrap-contracts"); require_check(values[i],visit); delete reason_visit; add_reason(values[i],"bootstrap:" d ":" domain_record[d],"domain-release",reason_visit) }
      next_version[d]="1.0.0"; domain_impact[d]=3
    }
  }
  fields="format domain impact contracts compatibility rationale migration"; field_count=split(fields,required," ")
  for(h in history_domain) {
    d=history_domain[h]
    for(i=1;i<=field_count;i++) if(!trailer_count[h,"release-" required[i]]) refuse("missing-release-trailer")
    if(trailer[h,"release-format"]!="1") refuse("unsupported-release-format")
    if(trailer[h,"release-domain"]!=d) refuse("release-domain-mismatch")
    impact=trailer[h,"release-impact"]; compatibility=trailer[h,"release-compatibility"]; migration=trailer[h,"release-migration"]
    if(!(impact in impacts)) refuse("invalid-release-impact")
    if(compatibility!~/^(compatible|breaking|unknown)$/ || compatibility=="unknown") refuse("unknown-compatibility")
    if(compatibility=="breaking" && (impact!="major" || migration=="none")) refuse("incompatible-impact")
    if(migration!="none") { if(!path(migration) || migration!~/^docs\// || migration_exists[h]!="blob") refuse("invalid-migration") }
    n=list(trailer[h,"release-contracts"],values)
    if(n<1) refuse("invalid-release-contracts")
    for(i=1;i<=n;i++) { if(check_domain[values[i]]!=d) refuse("invalid-release-contracts"); declared[h,values[i]]=1 }
    for(k in diff_path) {
      split(k,parts,SUBSEP); if(parts[1]!=d || parts[2]!=history_sha[h])continue
      p=parts[3]
      for(m=1;m<=map_count;m++) if((map_match[m]=="exact" && p==map_path[m]) || (map_match[m]=="prefix" && index(p,map_path[m])==1)) {
        n=list(map_checks[m],values)
        for(i=1;i<=n;i++) if(check_domain[values[i]]==d && !declared[h,values[i]]) refuse("release-contract-path-mismatch")
      }
    }
    if(trailer_count[h,"release-reverts"] && (!sha(trailer[h,"release-reverts"]) || revert_target[h]!=trailer[h,"release-reverts"])) refuse("invalid-revert-target")
  }
  # Pair cancellation is exact: both modes/blob directions and all paths match.
  for(order=1;order<=history_count;order++) {
    h=history_order[order]; if(!(h in revert_target))continue
    if(revert_category[h]=="released") { released_revert[h]=1; continue }
    target=history_domain[h] SUBSEP revert_target[h]
    if(!history_domain[target] || target==h || canceled[target] || canceled[h] || diff_count[target]!=diff_count[h]) { refuse("ambiguous-revert"); continue }
    inverse=1
    for(k in diff_path) { split(k,parts,SUBSEP); if(parts[1]==history_domain[h] && parts[2]==history_sha[h]) { p=parts[3]; if(!diff_path[target,p] || diff_value[h,p]!=diff_reverse[target,p]) inverse=0 } }
    if(!inverse) refuse("noninverse-revert")
    else { canceled[target]=1; canceled[h]=1 }
  }
  for(h in history_domain) if(!canceled[h]) {
    d=history_domain[h]; value=impacts[trailer[h,"release-impact"]]
    if(value>domain_impact[d]) domain_impact[d]=value
    compatibility=trailer[h,"release-compatibility"]; migration=trailer[h,"release-migration"]
    domain_compatibility[d]=(compatibility=="breaking" || domain_compatibility[d]=="breaking") ? "breaking" : compatibility
    if(migration!="none") { domain_migration[d,migration]=1; approval["migration"]=1 }
    if(trailer[h,"release-impact"]=="major")approval["major"]=1
  }
  for(d in baseline_kind) if(baseline_kind[d]=="semantic") {
    if(domain_delta[d] && domain_impact[d]>0) next_version[d]=increment(domain_version[d],domain_impact[d])
    else next_version[d]=""
  }
  # Promotion selection remains its own path comparison. A proposed domain
  # release also qualifies its effective declared contracts, even if source is
  # already on master; exact net-zero/none adds no release-only qualification.
  for(d in next_version) if(next_version[d]!="" && baseline_kind[d]=="semantic") {
    for(h in history_domain) if(history_domain[h]==d && !canceled[h]) {
      n=list(trailer[h,"release-contracts"],values)
      for(i=1;i<=n;i++) { require_check(values[i],visit); delete reason_visit; add_reason(values[i],d ":" history_sha[h],"domain-release",reason_visit) }
    }
  }
  for(c in evidence_seen) {
    if(!check_domain[c]) refuse("unknown-evidence-check")
    if(evidence_candidate[c]!=candidate || evidence_master[c]!=master || evidence_tree[c]!=merge_tree || evidence_rules[c]!=rules) refuse("evidence-identity-mismatch")
    if(evidence_tool[c]!=check_tool[c]) refuse("evidence-tool-mismatch")
  }
  for(c in selected) {
    if(!evidence_seen[c] && check_requirement[c]=="required") refuse("missing-required-evidence")
    else if(check_requirement[c]=="required" && evidence_state[c]!="verified") refuse("required-evidence-not-verified")
  }
  for(c in defects) { if(!check_domain[c]) refuse("unknown-defect-contract"); refuse("contract-defect") }
  domain_count=keys(baseline_kind,domains); error_count=keys(errors,error_keys); selected_count=keys(selected,checks); approval_count=keys(approval,approvals)
  changed=pending_source>0; for(d in next_version) if(next_version[d]!="") changed=1
  decision=error_count ? "refusal" : changed ? "candidate" : "no-op"
  out="{\"format\":1,\"decision\":" quote(decision) ",\"master\":" quote(master) ",\"candidate\":" quote(candidate) ",\"merge_tree\":" quote(merge_tree) ",\"rules\":" quote(rules) ",\"pending_source_commits\":" pending_source
  out=out ",\"git_version\":" quote(git_version) ",\"object_format\":" quote(object_format) ",\"git_command_digest\":" quote(git_command_digest) ",\"awk_command_digest\":" quote(awk_command_digest)
  out=out ",\"engine_digest\":" quote(engine_digest) ",\"classifier_digest\":" quote(classifier_digest) ",\"rules_digest\":" quote(rules_digest) ",\"baselines_digest\":" quote(baselines_digest) ",\"evidence_digest\":" quote(evidence_digest)
  out=out ",\"promotion_delta\":["; n=keys(promotion_path,promotion_paths)
  for(i=1;i<=n;i++) { p=promotion_paths[i]; if(i>1)out=out ","; out=out "{\"path\":" quote(p) ",\"status\":" quote(promotion_path[p]) ",\"owner\":" quote(promotion_owner[p]) "}" }
  out=out "],\"domains\":["
  for(i=1;i<=domain_count;i++) {
    d=domains[i]; if(i>1)out=out ","
    out=out "{\"domain\":" quote(d) ",\"baseline\":" quote(domain_base[d]) ",\"record\":" quote(domain_record[d]) ",\"reference\":" quote(domain_ref[d]) ",\"impact\":" quote(names[domain_impact[d]+0]) ",\"next_version\":" (next_version[d]!="" ? quote(next_version[d]) : "null") ",\"previous_version\":" quote(domain_version[d]) ",\"compatibility\":" (domain_compatibility[d]!="" ? quote(domain_compatibility[d]) : "null") ",\"migrations\":["
    delete migration_keys
    for(k in domain_migration) { split(k,parts,SUBSEP); if(parts[1]==d)migration_keys[parts[2]]=1 }
    n=keys(migration_keys,migration_paths)
    for(j=1;j<=n;j++) { if(j>1)out=out ","; out=out quote(migration_paths[j]) }
    out=out "],\"retired_previous_major\":" (domain_impact[d]==3 && baseline_kind[d]=="semantic" ? "true" : "false") "}"
  }
  out=out "],\"history\":["; comma=""
  for(i=1;i<=history_count;i++) { h=history_order[i]; out=out comma "{\"commit\":" quote(history_sha[h]) ",\"domain\":" quote(history_domain[h]) ",\"parent\":" quote(history_parent[h]) ",\"message_digest\":" quote(history_digest[h]) ",\"impact\":" quote(trailer[h,"release-impact"]) ",\"compatibility\":" quote(trailer[h,"release-compatibility"]) ",\"migration\":" quote(trailer[h,"release-migration"]) ",\"canceled\":" (canceled[h]?"true":"false") ",\"released_revert\":" (released_revert[h]?"true":"false") "}"; comma="," }
  out=out "],\"checks\":["
  for(i=1;i<=selected_count;i++) {
    c=checks[i]; if(i>1)out=out ","
    out=out "{\"id\":" quote(c) ",\"lane\":" quote(check_lane[c]) ",\"requiredness\":" quote(check_requirement[c]) ",\"state\":" quote(evidence_seen[c] ? evidence_state[c] : "unverified") ",\"expected_tool\":" quote(check_tool[c]) ",\"reference\":" quote(evidence_reference[c]) ",\"paths\":["
    delete path_keys
    for(k in reasons) { split(k,parts,SUBSEP); if(parts[1]==c)path_keys[parts[2]]=1 }
    n=keys(path_keys,reason_paths)
    for(j=1;j<=n;j++) { if(j>1)out=out ","; out=out quote(reason_paths[j]) }
    out=out "],\"selection_reasons\":["; delete selection_keys
    for(k in selection_reasons) { split(k,parts,SUBSEP); if(parts[1]==c)selection_keys[parts[2] SUBSEP parts[3]]=1 }
    n=keys(selection_keys,selection_values)
    for(j=1;j<=n;j++) { split(selection_values[j],parts,SUBSEP); if(j>1)out=out ","; out=out "{\"kind\":" quote(parts[1]) ",\"reference\":" quote(parts[2]) "}" }
    out=out "]}"
  }
  out=out "],\"unaffected_checks\":["; n=keys(check_domain,all_checks); comma=""
  for(i=1;i<=n;i++) if(!selected[all_checks[i]]) { out=out comma quote(all_checks[i]); comma="," }
  out=out "],\"approval_reasons\":["
  for(i=1;i<=approval_count;i++) { if(i>1)out=out ","; out=out quote(approvals[i]) }
  out=out "],\"reasons\":["
  for(i=1;i<=error_count;i++) { if(i>1)out=out ","; out=out quote(error_keys[i]) }
  out=out "]}"
  if(human) { print "Offline release preview: " decision; print "Promotion comparison: " master " -> " candidate; for(i=1;i<=domain_count;i++) { d=domains[i]; print d ": " (next_version[d]!="" ? next_version[d] : "no release") }; for(i=1;i<=error_count;i++) print "Refusal: " error_keys[i] }
  else print out
  exit error_count ? 1 : 0
}
