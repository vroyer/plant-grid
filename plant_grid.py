#!/usr/bin/env python
"""Plant Grid Farmware"""

import os
import json
import base64
import numpy as np
import requests

def log(message, message_type):
    'Send a message to the log.'
    log_message = '[plant-grid] ' + str(message)
    headers = {
        'Authorization': 'bearer {}'.format(os.environ['FARMWARE_TOKEN']),
        'content-type': "application/json"}
    payload = json.dumps(
        {"kind": "send_message",
            "args": {"message": log_message, "message_type": message_type}})
    requests.post(os.environ['FARMWARE_URL'] + 'api/v1/celery_script',
                    data=payload, headers=headers)

def get_env(key, type_=int):
    'Return the value of the namespaced Farmware input variable.'
    return type_(os.environ['{}_{}'.format(farmware_name, key)])

class Grid():
    'Add a grid of plants to the farm designer.'
    def __init__(self):
        API_TOKEN = os.environ['API_TOKEN']
        self.headers = {'Authorization': 'Bearer {}'.format(API_TOKEN),
                        'content-type': "application/json"}
        encoded_payload = API_TOKEN.split('.')[1]
        encoded_payload += '=' * (4 - len(encoded_payload) % 4)
        json_payload = base64.b64decode(encoded_payload).decode('utf-8')
        server = json.loads(json_payload)['iss']
        self.api_url = 'http{}:{}/api/'.format(
            's' if not any([h in server for h in ['localhost', '192.168.']])
            else '', server)

    def add_plant(self, x, y):
        'Add a plant through the FarmBot Web App API.'
        plant = {'x': str(x), 'y': str(y),
                 'radius': str(radius),
                 'name': name, 'pointer_type': 'Plant', 'openfarm_slug': slug}
        payload = json.dumps(plant)
        r = requests.post(self.api_url + 'points',
                          data=payload, headers=self.headers)

    def create_grid(self):
        'Create a coordinate grid based on the input options.'
        unit_grid = np.mgrid[0:x_num, 0:y_num]
        plant_grid = unit_grid
        plant_grid[0] = x_start + unit_grid[0] * x_step
        plant_grid[1] = y_start + unit_grid[1] * y_step
        xs, ys = np.vstack(map(np.ravel, plant_grid))
        return xs, ys

    def add_plants(self):
        'Add all plants in the grid to the farm designer.'
        X, Y = self.create_grid()
        for i in range(len(X)):
            self.add_plant(X[i], Y[i])
        log('{} plants added, starting at ({}, {}).'.format(len(X), X[0], Y[0]),
            'success')

if __name__ == '__main__':
    farmware_name = 'plant_grid'
    # Load inputs from Farmware page widget specified in manifest file
    x_num = get_env('x_num')
    y_num = get_env('y_num')
    x_step = get_env('x_step')
    y_step = get_env('y_step')
    x_start = get_env('x_start')
    y_start = get_env('y_start')
    radius = get_env('radius')
    name = get_env('name', str)
    slug = get_env('slug', str)
    
    grid = Grid()
    grid.add_plants()
