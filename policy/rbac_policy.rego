package kubernetes.admission

deny[reason] {
  input.kind.kind == "RoleBinding"
  some i
  rb := input
  # if roleRef is ClusterRole or name contains "cluster-admin" or "*"
  rb.roleRef.kind == "ClusterRole"
  reason = sprintf("RoleBinding %v in namespace %v references a ClusterRole (avoid ClusterRole in tenant namespace)", [rb.metadata.name, rb.metadata.namespace])
}

deny[reason] {
  input.kind.kind == "Role"
  r := input
  some i
  rule := r.rules[_]
  # detect wildcard verbs or resources - too permissive
  rule.verbs[_] == "*" 
  reason = sprintf("Role %v in namespace %v has wildcard verb '*'", [r.metadata.name, r.metadata.namespace])
}

deny[reason] {
  input.kind.kind == "Role"
  r := input
  some i
  rule := r.rules[_]
  rule.resources[_] == "*" 
  reason = sprintf("Role %v in namespace %v has wildcard resource '*'", [r.metadata.name, r.metadata.namespace])
}

deny[reason] {
  input.kind.kind == "ClusterRoleBinding"
  crb := input
  reason = sprintf("ClusterRoleBinding %v detected - review privileges", [crb.metadata.name])
}

deny[reason] {
  input.kind.kind == "RoleBinding"
  rb := input
  # disallow binding to system:masters group via subjects (common mistake)
  some i
  subj := rb.subjects[_]
  subj.kind == "Group"
  subj.name == "system:masters"
  reason = sprintf("RoleBinding %v binds group system:masters", [rb.metadata.name])
}
