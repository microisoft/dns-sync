dns-sync
========

SERVER
========

<pre>

options {
        directory       "/var/named";
        dump-file       "/var/named/data/cache_dump.db";
        statistics-file "/var/named/data/named_stats.txt";
        memstatistics-file "/var/named/data/named_mem_stats.txt";
        recursion yes;

        dnssec-enable yes;
        dnssec-validation yes;
        dnssec-lookaside auto;

        /* Path to ISC DLV key */
        bindkeys-file "/etc/named.iscdlv.key";

        managed-keys-directory "/var/named/dynamic";
        allow-transfer { 11.11.11.2; };
        notify          yes;

        also-notify {
                11.11.11.2;
                };
        };

key "key1" {
                algorithm hmac-md5;
                secret "Base64 encode pass"; #пароль
                           };

                server 11.11.11.2 { #ip адрес вторичного dns сервера
                keys {
                        key1;
                        };
                };

logging {
        channel default_debug {
                file "data/named.run";
                severity dynamic;
        };
};


</pre>



SLAVE
========
<pre>
options {
        directory "/var/cache/bind";

        dnssec-validation auto;

        auth-nxdomain no;    # conform to RFC1035
        listen-on-v6 { any; };

        allow-update { 11.11.11.1; };
        allow-notify { 11.11.11.1; };

        forwarders {
                11.11.11.1;
                //213.133.98.98;
                //213.133.99.99;
                //213.133.100.100;
        };

        allow-query             { any; };

        allow-transfer  {

                        11.11.11.1;

                        };


        };

        key "key1" {
                algorithm hmac-md5;
                secret "Base64 encode pass";
                           };

                server 11.11.11.1 { #ip адрес первичного dns сервера
                keys {
                       key1;
                        };
                };

       logging {

        channel notify_log      {

        file "/var/log/bind/bind-notify.log" versions 3 size 1M;
        severity info;
        print-category yes;
        print-severity yes;
        print-time yes;
                                };

        category notify       { notify_log; };

        };
</pre>
