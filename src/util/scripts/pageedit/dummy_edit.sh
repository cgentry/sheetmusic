#
#:title Dummy script that just prints vars to /tmp/dummy.txt
# This doesn't do anything at all. It just dumps and exits.
# Created so you can see what you are getting when you write a script
# NOTE: os filters by 'type'. you can have either:
# unix - generic covers mac, linux and freebsd
# linux - linux only 
# freebsd
# macos
# win - MS Windows only. 
#:os unix

>&2 echo "Dummy script test"
echo Script variables for "${0}" 
echo $@ 