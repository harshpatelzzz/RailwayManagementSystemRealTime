<?php
/**
 * Twitter API Handler
 * Handles posting responses to Twitter
 */

require_once 'config.php';

// Check if TwitterOAuth is available
if (file_exists(__DIR__ . '/../vendor/autoload.php')) {
    require_once __DIR__ . '/../vendor/autoload.php';
}

class TwitterAPI {
    private $connection;
    private $available;
    
    public function __construct() {
        $this->available = class_exists('Abraham\TwitterOAuth\TwitterOAuth');
        
        if ($this->available) {
            try {
                $this->connection = new \Abraham\TwitterOAuth\TwitterOAuth(
                    TWITTER_CONSUMER_KEY,
                    TWITTER_CONSUMER_SECRET,
                    TWITTER_ACCESS_TOKEN,
                    TWITTER_ACCESS_TOKEN_SECRET
                );
            } catch (Exception $e) {
                $this->available = false;
                error_log("TwitterOAuth initialization failed: " . $e->getMessage());
            }
        }
    }
    
    /**
     * Post a reply to a tweet
     * @param int $tweet_id Original tweet ID
     * @param string $response Response text
     * @return array Result with status and message
     */
    public function replyToTweet($tweet_id, $response) {
        if (!$this->available) {
            return [
                'status' => 'error',
                'message' => 'TwitterOAuth library not installed. Run: composer install'
            ];
        }
        
        try {
            // Twitter API v2 endpoint for posting tweets
            $data = [
                'text' => $response,
                'reply' => [
                    'in_reply_to_tweet_id' => $tweet_id
                ]
            ];
            
            $result = $this->connection->post('tweets', $data);
            
            if ($this->connection->getLastHttpCode() == 201) {
                return [
                    'status' => 'success',
                    'message' => 'Response posted successfully',
                    'tweet_id' => $result->data->id ?? null
                ];
            } else {
                $errors = $this->connection->getLastBody()->errors ?? [];
                $error_message = isset($errors[0]) ? $errors[0]->message : 'Unknown error';
                
                return [
                    'status' => 'error',
                    'message' => $error_message
                ];
            }
        } catch (Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage()
            ];
        }
    }
    
    /**
     * Send a direct message (alternative to public reply)
     * @param string $user_id Twitter user ID
     * @param string $message Message text
     * @return array Result with status and message
     */
    public function sendDirectMessage($user_id, $message) {
        if (!$this->available) {
            return [
                'status' => 'error',
                'message' => 'TwitterOAuth library not installed. Run: composer install'
            ];
        }
        
        try {
            $data = [
                'event' => [
                    'type' => 'message_create',
                    'message_create' => [
                        'target' => [
                            'recipient_id' => $user_id
                        ],
                        'message_data' => [
                            'text' => $message
                        ]
                    ]
                ]
            ];
            
            $result = $this->connection->post('direct_messages/events/new', $data);
            
            if ($this->connection->getLastHttpCode() == 200) {
                return [
                    'status' => 'success',
                    'message' => 'Direct message sent successfully'
                ];
            } else {
                return [
                    'status' => 'error',
                    'message' => 'Failed to send direct message'
                ];
            }
        } catch (Exception $e) {
            return [
                'status' => 'error',
                'message' => $e->getMessage()
            ];
        }
    }
}

// Usage example (uncomment to test)
/*
$twitter = new TwitterAPI();
$result = $twitter->replyToTweet(1234567890, "Thank you for your feedback. We are looking into this issue.");
print_r($result);
*/
?>

