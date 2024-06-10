import threading 
import queue

"""
a thread commands listener, vai houvir por métodos automáticos. 
Mas estes métodos automáticos, só vão vir caso a thread output-listeners 
esteja ainda a funcionar, de outro modo não existe possibilidade de receber 
comandos.

Desta forma caso recebamos informação que a thread acabou
e que não há mais eventos para ler da queue, então podemos acabar.
"""
def commands_listener_func(shared_queue):
	thread_pool = ThreadPoolExecutor(max_workers=3)
	while True:
		message = shared_queue.get() # blocks
		if message == 'method':
			print('thread received method')
		if message = 'Done':
			print('the other thread finished')
	pass

def output_listener_func(shared_queue):
	while True:
		for i in range 10000000:
			if i % 5000000 == 0:
				shared_queue.put('method')
		shared_queue.put('Done')
		break
	pass

if __name__ == 'main':
	shared_q = queue.Queue()
	cl = threading.Thread(target = commands_listener_func, args=(shared_q))
	ol = threading.Thread(target = output_listener_func, args=(shared_q))

	cl.start()
	ol.start()
