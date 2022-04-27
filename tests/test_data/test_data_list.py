import uuid


node_list = [
    {
        'id': '7d71cd95-2e98-4f35-a070-96a99958d7ac', 
        'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
        'node_id': 'A', 
        'name': 'Mobitel-1', 
        'type': 'Central Hub',
        'latitude': 10.456, 
        'longitude': 50.852, 
        'radius': None
        }, 
        {
            'id': '96e2a550-27c4-4493-ad3d-65bea9e63fcf', 
            'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
            'node_id': 'B', 
            'name': 'M-Region1', 
            'type': 'Regional Hub', 
            'latitude': 9.456, 
            'longitude': 51.852, 
            'radius': None
            }, 
            {
                'id': '4af7aab3-f853-498b-90d3-95293b05f532', 
                'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                'node_id': 'D', 
                'name': 'M-Tower1', 
                'type': 'Tower', 
                'latitude': 37.773972, 
                'longitude': -122.43129, 
                'radius': 16093.4
                }, 
                {
                    'id': 'ad4bc6ab-719d-4a7f-a00e-bde74c425f88', 
                    'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                    'node_id': 'E', 
                    'name': 'M-Tower2', 
                    'type': 'Tower', 
                    'latitude': 37.804363, 
                    'longitude': -122.4111, 
                    'radius': 16093.4
                    }, 
                    {
                        'id':'7831185e-9c94-48c6-97fd-9e414d2a07c1', 
                        'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                        'node_id': 'C', 
                        'name': 'M-Region2', 
                        'type': 'Regional Hub', 
                        'latitude': 8.456, 
                        'longitude': 52.852, 
                        'radius': None
                        }, 
                        {
                            'id': '22c8c042-c553-4bb9-833d-cec227be6c72',
                            'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                            'node_id': 'F', 
                            'name': 'M-Tower3', 
                            'type': 'Tower', 
                            'latitude': 37.6879, 
                            'longitude': -122.4702, 
                            'radius': 16093.4
                            }, 
                            {
                                'id': '16ea60e0-8104-4068-93ce-29abc8d801d1',
                                'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                                'node_id': 'G', 
                                'name': 'M-Tower4', 
                                'type': 'Tower', 
                                'latitude': 13.456, 
                                'longitude': 56.852, 
                                'radius': 9.0
                                }, 
                                {
                                    'id': 'a0f9e46a-2af7-427a-a5d7-95e06ac97f3c',
                                    'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7',
                                    'node_id': 'H', 
                                    'name': 'M-Tower5', 
                                    'type': 'Tower', 
                                    'latitude': 14.456, 
                                    'longitude': 57.852, 
                                    'radius': 8.0
                                    }, 
                                    {
                                        'id':'f7c7d4c1-dd46-4070-ba07-31b26e3add9d', 
                                        'network_id': '27c50c4f-89ae-4ef4-91a9-918496fe15d7', 
                                        'node_id': 'I', 
                                        'name': 'M-Tower6', 
                                        'type': 'Tower', 
                                        'latitude': 15.456, 
                                        'longitude': 58.852, 
                                        'radius': 7.0
            }]

edge_list = [
    ('A', 'B', {}), 
    ('A', 'C', {}), 
    ('B', 'D', {}), 
    ('B', 'E', {}), 
    ('C', 'F', {}), 
    ('C', 'G', {}), 
    ('C', 'H', {}), 
    ('C', 'I', {})]