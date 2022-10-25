# Name: Philipp Plamper
# Date: 19. september 2022

# parameter for temporal graph 

# host + port
host = 'http://localhost:7474'

# username and password for neo4j instance
user = 'neo4j'
passwd = '1234'

# names for neo4j databases
db_name_temporal = 'modeltemporal'
db_name_smash = 'modelsmash'
db_name_rev = 'modeltransformback'

# define fault tolerance for intensity trend 
upper_limit = 1.025 # above considered as increasing intensity
lower_limit = 0.975 # below considered as decreasing intensity