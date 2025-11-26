"""
Graph Database Service for Neo4j
Maps entity relationships and attack paths
"""
from typing import Dict, Any, List, Optional
import os

try:
    from neo4j import GraphDatabase
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    print("⚠️  Neo4j driver not available. Graph analysis will be limited.")

class GraphAnalyzer:
    """Service for analyzing entity relationships using Neo4j"""
    
    def __init__(self):
        self.driver = None
        self.uri = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "soc_password")
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize Neo4j connection"""
        if not NEO4J_AVAILABLE:
            return
        
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Test connection (with timeout)
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✅ Neo4j connection established")
        except Exception as e:
            # Don't fail startup if Neo4j is unavailable
            print(f"⚠️  Could not connect to Neo4j (will retry on use): {e}")
            self.driver = None
    
    def create_incident_graph(self, incident_data: Dict[str, Any]) -> bool:
        """
        Create graph nodes and relationships for an incident
        """
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                # Create or update User node
                if incident_data.get('user_id'):
                    session.run("""
                        MERGE (u:User {id: $user_id})
                        SET u.email = $email, u.name = $name
                    """, user_id=incident_data['user_id'],
                        email=incident_data.get('user_email', ''),
                        name=incident_data.get('user_name', ''))
                
                # Create or update IP nodes
                if incident_data.get('source_ip'):
                    session.run("""
                        MERGE (ip:IP {address: $ip})
                        SET ip.last_seen = datetime(), ip.is_malicious = $is_malicious
                    """, ip=incident_data['source_ip'],
                        is_malicious=incident_data.get('severity') in ['HIGH', 'CRITICAL'])
                
                if incident_data.get('destination_ip'):
                    session.run("""
                        MERGE (ip:IP {address: $ip})
                        SET ip.last_seen = datetime()
                    """, ip=incident_data['destination_ip'])
                
                # Create Incident node
                session.run("""
                    MERGE (inc:Incident {id: $incident_id})
                    SET inc.severity = $severity,
                        inc.threat_type = $threat_type,
                        inc.detected_at = datetime($detected_at),
                        inc.anomaly_score = $anomaly_score
                """, incident_id=incident_data['incident_id'],
                    severity=incident_data.get('severity', 'MEDIUM'),
                    threat_type=incident_data.get('threat_type', 'Unknown'),
                    detected_at=incident_data.get('detected_at'),
                    anomaly_score=incident_data.get('anomaly_score', 0.0))
                
                # Create relationships
                if incident_data.get('user_id') and incident_data.get('source_ip'):
                    session.run("""
                        MATCH (u:User {id: $user_id})
                        MATCH (ip:IP {address: $source_ip})
                        MERGE (u)-[:ACCESSED_FROM]->(ip)
                    """, user_id=incident_data['user_id'],
                        source_ip=incident_data['source_ip'])
                
                if incident_data.get('source_ip') and incident_data.get('incident_id'):
                    session.run("""
                        MATCH (ip:IP {address: $source_ip})
                        MATCH (inc:Incident {id: $incident_id})
                        MERGE (ip)-[:CAUSED]->(inc)
                    """, source_ip=incident_data['source_ip'],
                        incident_id=incident_data['incident_id'])
                
                if incident_data.get('source_ip') and incident_data.get('destination_ip'):
                    session.run("""
                        MATCH (src:IP {address: $source_ip})
                        MATCH (dst:IP {address: $destination_ip})
                        MERGE (src)-[:CONNECTED_TO]->(dst)
                    """, source_ip=incident_data['source_ip'],
                        destination_ip=incident_data['destination_ip'])
                
                return True
        except Exception as e:
            print(f"Error creating incident graph: {e}")
            return False
    
    def get_related_entities(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Get all entities related to a given entity
        """
        if not self.driver:
            return {'error': 'Neo4j not available'}
        
        try:
            with self.driver.session() as session:
                if entity_type == 'ip':
                    result = session.run("""
                        MATCH (ip:IP {address: $ip})
                        OPTIONAL MATCH (ip)-[r]-(related)
                        RETURN type(r) as relationship, labels(related) as entity_type, 
                               properties(related) as entity_props
                        LIMIT 50
                    """, ip=entity_id)
                    
                    relationships = []
                    for record in result:
                        relationships.append({
                            'relationship': record['relationship'],
                            'entity_type': record['entity_type'],
                            'entity': record['entity_props']
                        })
                    
                    return {'entity': entity_id, 'relationships': relationships}
                
                elif entity_type == 'user':
                    result = session.run("""
                        MATCH (u:User {id: $user_id})
                        OPTIONAL MATCH (u)-[r]-(related)
                        RETURN type(r) as relationship, labels(related) as entity_type,
                               properties(related) as entity_props
                        LIMIT 50
                    """, user_id=entity_id)
                    
                    relationships = []
                    for record in result:
                        relationships.append({
                            'relationship': record['relationship'],
                            'entity_type': record['entity_type'],
                            'entity': record['entity_props']
                        })
                    
                    return {'entity': entity_id, 'relationships': relationships}
        except Exception as e:
            return {'error': str(e)}
    
    def find_attack_path(self, source_ip: str, target_ip: str) -> Dict[str, Any]:
        """
        Find attack path between two IPs
        """
        if not self.driver:
            return {'error': 'Neo4j not available'}
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH path = shortestPath(
                        (src:IP {address: $source_ip})-[*..10]-(dst:IP {address: $target_ip})
                    )
                    RETURN path, length(path) as path_length
                    LIMIT 1
                """, source_ip=source_ip, target_ip=target_ip)
                
                for record in result:
                    return {
                        'path_found': True,
                        'path_length': record['path_length'],
                        'path': str(record['path'])
                    }
                
                return {'path_found': False}
        except Exception as e:
            return {'error': str(e)}
    
    def get_compromised_hosts(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get all hosts accessed by a potentially compromised user
        """
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (u:User {id: $user_id})-[:ACCESSED_FROM]->(ip:IP)
                    WHERE ip.is_malicious = true
                    RETURN DISTINCT ip.address as ip, ip.last_seen as last_seen
                """, user_id=user_id)
                
                hosts = []
                for record in result:
                    hosts.append({
                        'ip': record['ip'],
                        'last_seen': record['last_seen']
                    })
                
                return hosts
        except Exception as e:
            print(f"Error getting compromised hosts: {e}")
            return []

# Global instance
graph_analyzer = GraphAnalyzer()

