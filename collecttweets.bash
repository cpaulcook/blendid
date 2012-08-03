# Set TWITTER_USERNAME and PASSWORD appropriately...

while true; do
curl -d @neos.track https://stream.twitter.com/1/statuses/filter.json -uTWITTER_USERNAME:PASSWORD > `date +%y%m%d%H%M%S`.json;
echo "disconnected at `date`"
sleep 60;
done
