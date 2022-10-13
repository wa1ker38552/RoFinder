import requests

class Searcher:
  def __init__(self, user, universe):
    request = requests.post('https://presence.roblox.com/v1/presence/users', json={'userIds': [user]}).json()
    if not request['userPresences'][0]['userPresenceType'] == 2:
      # in-game
      self.server_id = None

    data = [{
      'format': "png",
      'requestId': f"{user}::AvatarHeadshot:150x150:png:regular",
      'size': "150x150",
      'targetId': user,
      'token': "",
      'type': "AvatarHeadShot"
    }]
    request = requests.post('https://thumbnails.roblox.com/v1/batch', json=data).json()['data'][0]['imageUrl']
    self.image_id = request.split('/')[3]
    
    # process user
    self.universe = universe
    # search servers
    resp = self.search_public_servers()
    self.player_tokens = []
    for ser in resp: self.player_tokens.extend(ser['tokens'])

    # batch profiles
    data = [{'type': 'avatarHeadshot', 'token': id, 'size': '150x150', 'isCircular': True} for id in self.player_tokens]
    
    # process request id's
    raw = []
    if len(data) > 100:
      raw.extend(self.batch_thumbnails(data[:len(data)%100]))
      x = len(data)%100
      for i in range(int((len(data)-(len(data)%100))/100)):
        raw.extend(self.batch_thumbnails(data[x:x+100]))
        x += 100
    else:
      raw.extend(self.batch_thumbnails(data))

    for i, img in enumerate(raw):
      if img['imageUrl'].split('/')[3] == self.image_id:
        # found matching id's
        print(f'Match found: {self.image_id}. Searching server id')
        for ser in resp:
          if self.player_tokens[i] in ser['tokens']:
            self.server_id = ser['server_id']
            return

  def get_id(self):
    if self.server_id is None:
      return None
    else:
      return self.server_id

  def batch_thumbnails(self, ids):
    data = [{'type': 'avatarHeadshot', 'token': id['token'], 'size': '150x150', 'isCircular': True} for id in ids]
    request = requests.post('https://thumbnails.roblox.com/v1/batch', json=data).json()
    # print(request)
    print(f'{len(request["data"])} thumbnails batched.')

    return request['data']

  def search_public_servers(self, data=[], next_page=None):
    # recursively collect usertokens
    print(f'Searching servers: {next_page}, {len(data)}.')
    if next_page is None:
      request = requests.get(f'https://games.roblox.com/v1/games/{self.universe}/servers/Public?limit=100').json()
    else:
      request = requests.get(f'https://games.roblox.com/v1/games/{self.universe}/servers/Public?limit=100&cursor={next_page}').json()
    next_page = request['nextPageCursor']

    for server in request['data']:
      data.append({'server_id': server['id'], 'tokens': server['playerTokens']})

    # check next page
    if next_page is None:
      return data
    else:
      return self.search_public_servers(data, next_page)
    


search = Searcher(USERID, GAMEID)
print(search.server_id)
