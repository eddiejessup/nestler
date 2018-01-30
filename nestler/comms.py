from ipykernel.comm import comms


INTERACTIVITY_TARGET_NAME = 'interactivity'
INTERACTIVITY_COMM_ID = 'interactivity'
NEW_COMM_COMM_ID = 'new_comm'


def open_register_target_comm(client, comm_id=NEW_COMM_COMM_ID):
    client.comm_open(
        comm_id=comm_id,
        target_name=comms.REGISTER_TARGET_COMM_TARGET_NAME,
    )


def interactivity_comm_open(comm, open_msg, comm_id=INTERACTIVITY_COMM_ID):
    # Set the shell's interactivity mode.
    def msg_callback(msg):
        data = msg['content']['data']
        value = data['value']
        comm.kernel.shell.ast_node_interactivity = value
    comms.configure_comm(comm, comm_id=comm_id,
                         msg_callback=msg_callback)


def open_interactivity_comm(client, new_comm_comm_id=NEW_COMM_COMM_ID,
                            inter_target_name=INTERACTIVITY_TARGET_NAME,
                            inter_comm_id=INTERACTIVITY_COMM_ID):
    # Register the interactivity comm handler.
    client.comm_message(
        comm_id=new_comm_comm_id,
        data={
            'new_target_name': inter_target_name,
            'comm_open_callback': 'nestler.comms.interactivity_comm_open',
        }
    )
    # Open a new comm.
    client.comm_open(
        comm_id=inter_comm_id,
        target_name=inter_target_name,
    )


def set_interactivity(client, value, comm_id=INTERACTIVITY_COMM_ID):
    client.comm_message(
        comm_id=comm_id,
        data={'value': value},
    )
