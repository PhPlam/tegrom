# Name: Philipp Plamper
# Date: 19. september 2022

# parameter for temporal graph 

# host + port
host = 'http://localhost:7474'

# username and password for neo4j instance
user = 'neo4j'
passwd = '1234'

# names for neo4j databases
db_name_temporal = 'modeltemporaltest'
db_name_smash = 'modelsmashtest'
db_name_rev = 'modeltransformback'

# define threshold for intensity trend 
upper_limit = 1.025 # above considered as increasing intensity
lower_limit = 0.975 # below considered as decreasing intensity