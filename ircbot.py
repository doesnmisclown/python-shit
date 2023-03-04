import irc.client
target = "#bindev"
def on_connect(connection,event):
  if irc.client.is_channel(target):
    connection.join(target)
def on_join(connection,event):
  print(event)
  if not "u5er" in event.source: return
  connection.privmsg(target,f"{event.source.split('!~')[0]} вошел в чат")
def on_quit(connection,event):
  print(event)
  if not "u5er" in event.source: return
  connection.privmsg(target,f"{event.source.split('!~')[0]} вышел с чата.")
reactor = irc.client.Reactor()
c = reactor.server().connect("irc.libera.chat",6667,"NotifyBot")
c.add_global_handler("welcome",on_connect)
c.add_global_handler("join",on_join)
c.add_global_handler("quit",on_quit)
reactor.process_forever()