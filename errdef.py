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
错误描述：连接导航时，使用的 okhttp 三方库崩溃。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...com.android.okhttp..."}
复现版本：Android-2.8.29
"""
ERR_NAV_OKHTTP_CRASH = 'NAV-OKHTTP-CRASH'
"""
错误描述：连接导航时，使用的 okhttp 三方库崩溃。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...lang.NullPointerException..."}
复现版本：Android-2.8.29
"""
ERR_NAV_NULLPOINTER = 'NAV-NULLPOINTER'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...libcore.io.Streams.readAsciiLine..."}
复现版本：Android-2.8.29
"""
ERR_NAV_READASCIILINE = 'NAV-READASCIILINE'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...java.io.BufferedInputStream.streamClosed..."}
复现版本：Android-2.8.29
"""
ERR_NAV_STREAMCLOSED = 'NAV-DNS-STREAMCLOSED'
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
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...Stream closed..."}
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
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketException: recvfrom failed: ETIMEDOUT..."}
复现版本：Android-2.8.29
"""
ERR_NAV_ETIMEDOUT = 'NAV-ETIMEDOUT'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketException: Software caused connection abort..."}
复现版本：Android-2.8.29
"""
ERR_NAV_SOFTWARE_ABORT = 'NAV-SOFTWARE-ABORT'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...ProtocolException: Too many follow-up requests: 21
        at com.android.okhttp.internal.huc.HttpURLConnectionImpl.getResponse(HttpURLConnectionImpl.java:451)..."}
复现版本：Android-2.8.29
"""
ERR_NAV_OKHTTP_TOOMANY_FOLLOWUP = 'NAV-OKHTTP-TOOMANY-FOLLOWUP'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketException: Network is unreachable
        at java.net.PlainSocketImpl.socketConnect(Native Method)..."}
复现版本：Android-2.8.29
"""
ERR_NAV_SOCKET_NETWORK_UNREACHABLE = 'NAV-SOCKET-NETWORK-UNREACHABLE'
"""
错误描述：原因未知。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...SocketException: Network is unreachable
        at java.net.PlainSocketImpl.socketConnect(Native Method)..."}
复现版本：Android-2.8.29
"""
ERR_NAV_CON_NETWORK_UNREACHABLE = 'NAV-CON-NETWORK-UNREACHABLE'
"""
错误描述：数字转换格式错误。
认定条件："tag":"L-get_navi-R", "meta":{"stacks":"...java.lang.NumberFormatException..."}
复现版本：Android-2.8.31
"""
ERR_NAV_NUMBER_FORMAT_EXCEPTION = 'NAV-NUMBER-FORMAT-EXCEPTION'