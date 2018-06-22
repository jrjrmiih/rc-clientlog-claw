"""
multi types of error definitions file.
"""

# navi error types.
"""
错误描述：导航连接失败，打印不出崩溃栈，原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":""}
复现版本：Android-2.8.29
"""
ERR_NAV_STACKS_EMPTY = 'NAV-STACKS-EMPTY'
"""
错误描述：导航地址 DNS 解析失败。
认定条件："tag":"L-get_navi-R", "meta":{"ip":"null"}
复现版本：Android-2.8.29
"""
ERR_NAV_DNS_FAILED = 'NAV-DNS-FAILED'
"""
错误描述：导航连接失败，原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...Connection refused..."}
复现版本：Android-2.8.29
"""
ERR_NAV_CON_REFUSED = 'NAV-CON-REFUSED'
"""
错误描述：导航连接失败，连接超时。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...connect timed out..."}
复现版本：Android-2.8.29
"""
ERR_NAV_CON_TIMEOUT = 'NAV-CON-TIMEOUT'
"""
错误描述：导航连接失败，原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...failed to connect to..."}
复现版本：Android-2.8.29
"""
ERR_NAV_CON_FAILED = 'NAV-CON-FAILED'
"""
错误描述：导航连接失败，原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...failed to connect to..."}
复现版本：Android-2.8.29
"""
ERR_NAV_STREAM_CLOSED = 'NAV-STREAM-CLOSED'
"""
错误描述：socket 连接超时。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketTimeoutException..."}
复现版本：Android-2.8.29
"""
ERR_NAV_SOCKET_TIMEOUT = 'NAV-SOCKET-TIMEOUT'
"""
错误描述：连接被重置。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketException: Connection reset..."}
复现版本：Android-2.8.29
"""
ERR_NAV_CON_RESET = 'NAV-CON-RESET'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...unexpected end of stream on Connection..."}
复现版本：Android-2.8.29
"""
ERR_NAV_END_STREAM = 'NAV-END-STREAM'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...recvfrom failed: ECONNRESET..."}
复现版本：Android-2.8.29
"""
ERR_NAV_ECONNRESET = 'NAV-ECONNRESET'