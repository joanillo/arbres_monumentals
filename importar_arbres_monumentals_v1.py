# encoding: utf-8

import json #parsejar JSON

import termios, fcntl, sys, os #script interactiu

import requests #cercar node
import jxmlease

from osmapi import OsmApi #create, update node

overpass_url = "http://overpass-api.de/api/interpreter"

#---
def press_key():
	fd = sys.stdin.fileno()

	oldterm = termios.tcgetattr(fd)
	newattr = termios.tcgetattr(fd)
	newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
	termios.tcsetattr(fd, termios.TCSANOW, newattr)

	oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
	fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

	try:
		while 1:
			try:
				c = sys.stdin.read(1)
				#print "Got character", repr(c)
				return c;
			except IOError: pass
	finally:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
#---

with open('arbres.json', 'r') as f:
    arbres_dict = json.load(f)

num_changeset = 1
for arbre in arbres_dict:

	name = arbre['name'];
	lat = float(arbre['lat']);
	lon = float(arbre['lon']);
	species = arbre['species'];
	species_ca = arbre['species:ca'];
	note = arbre['note'];
	print("=================================")
	print(num_changeset)
	print("=================================")
	print name
	print "(",lat,",",lon,")";

	#cerquem els arbres que tenim, per actualitzar o per inserir
	overpass_query = "node[natural=tree](around:50,%f,%f); out;" % (lat, lon)
	#print overpass_query;
	response = requests.get(overpass_url, params={'data': overpass_query})
	print response.content;
	#volem recuperar el id del node que hem trobat
	root = jxmlease.parse(response.content)
	num = 0	
	for i in root['osm'].find_nodes_with_tag('node', recursive=False):
		print "node: " + i.get_xml_attr("id") + " en les immediacions"
		num+=1;
		print("ACTUALITZACIÓ\n=============");
		print(name)
		print(species)
		print(species_ca)
		print(note)

		print('Vols actualitzar les dades (y/n)');
		tecla = press_key();
		#print(tecla)
		if (tecla=='y'):
			print('Anem a actualitzar')
			MyApi = OsmApi(passwordfile="/home/joan/projectes/arbres_monumentals/.password")

			changeset_comment = '{"comment": "Modificació arbre monumental #%s"}' % (str(num_changeset))
			changeset_comment_json = json.loads(changeset_comment)
			MyApi.ChangesetCreate(changeset_comment_json)
			node = MyApi.NodeGet(i.get_xml_attr("id"))
			tags = node["tag"]
			tags[u"natural"] = u"tree"
			tags[u"name"] = name
			tags[u"species"] = species
			tags[u"species:ca"] = species_ca
			tags[u"note"] = note

			print(MyApi.NodeUpdate(node))
			MyApi.ChangesetClose()
			MyApi.flush()
			print ("arbre actualitzat");
			num_changeset = num_changeset + 1;
		else:
			print('No volem actualitzar')

	if (num==0):
		print("\n\nINSERCIÓ\n========")

		MyApi = OsmApi(passwordfile="/home/joan/projectes/arbres_monumentals/.password")

		changeset_comment = '{"comment": "Inserció arbre monumental #%s"}' % (str(num_changeset))
		changeset_comment_json = json.loads(changeset_comment)
		MyApi.ChangesetCreate(changeset_comment_json)
		data = '{"lat":%f, "lon":%f, "tag": { "natural": "tree", "name": "%s", "species": "%s", "species:ca": "%s", "note": "%s" }}' % (lat, lon, name, species, species_ca, note)
		data_json = json.loads(data)
		print(data_json)
		print(MyApi.NodeCreate(data_json))
		MyApi.ChangesetClose()
		MyApi.flush()
		print ("arbre inserit");
		num_changeset = num_changeset + 1;




