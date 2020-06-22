# Description
* Members are stored by etcd
* There is system to discover new members

## User interface
* Manage the members
* Refresh member list
* Add member from discovery (or manually?)
* Remove member
* Disconnected members are listed but grayed out

## Failures
* In case of failure during removal, etcd might need to [restart from majority failure](https://etcd.io/docs/v3.4.0/op-guide/runtime-configuration/#restart-cluster-from-majority-failure)

# Questions
* Cluster naming
* If member changes IP how to not rediscover him?
* When does the cluster start?
* How to keep added members in the cluster?
