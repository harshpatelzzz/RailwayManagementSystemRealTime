<?php
/**
 * Telegram API Handler
 * Handles sending responses to Telegram users
 */

require_once 'config.php';

class TelegramAPI {
    private $bot_token;
    private $api_url;
    
    public function __construct() {
        $this->bot_token = getenv('TELEGRAM_BOT_TOKEN') ?: '';
        $this->api_url = "https://api.telegram.org/bot{$this->bot_token}";
        
        if (empty($this->bot_token)) {
            error_log("Telegram Bot Token not configured");
        }
    }
    
    /**
     * Send a message to a Telegram user
     * @param int $chat_id Telegram chat ID
     * @param string $message Message text
     * @return array Result with status and message
     */
    public function sendMessage($chat_id, $message) {
        if (empty($this->bot_token)) {
            return [
                'status' => 'error',
                'message' => 'Telegram Bot Token not configured'
            ];
        }
        
        try {
            $url = $this->api_url . "/sendMessage";
            
            $data = [
                'chat_id' => $chat_id,
                'text' => $message,
                'parse_mode' => 'HTML'
            ];
            
            $ch = curl_init($url);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($http_code == 200) {
                $result = json_decode($response, true);
                if ($result && $result['ok']) {
                    return [
                        'status' => 'success',
                        'message' => 'Message sent successfully',
                        'message_id' => $result['result']['message_id'] ?? null
                    ];
                } else {
                    return [
                        'status' => 'error',
                        'message' => $result['description'] ?? 'Unknown error'
                    ];
                }
            } else {
                return [
                    'status' => 'error',
                    'message' => "HTTP Error: $http_code"
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
     * Send a reply to a specific message
     * @param int $chat_id Telegram chat ID
     * @param int $message_id Message ID to reply to
     * @param string $message Reply text
     * @return array Result with status and message
     */
    public function sendReply($chat_id, $message_id, $message) {
        if (empty($this->bot_token)) {
            return [
                'status' => 'error',
                'message' => 'Telegram Bot Token not configured'
            ];
        }
        
        try {
            $url = $this->api_url . "/sendMessage";
            
            $data = [
                'chat_id' => $chat_id,
                'text' => $message,
                'reply_to_message_id' => $message_id,
                'parse_mode' => 'HTML'
            ];
            
            $ch = curl_init($url);
            curl_setopt($ch, CURLOPT_POST, 1);
            curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($data));
            curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
            
            $response = curl_exec($ch);
            $http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
            curl_close($ch);
            
            if ($http_code == 200) {
                $result = json_decode($response, true);
                if ($result && $result['ok']) {
                    return [
                        'status' => 'success',
                        'message' => 'Reply sent successfully'
                    ];
                } else {
                    return [
                        'status' => 'error',
                        'message' => $result['description'] ?? 'Unknown error'
                    ];
                }
            } else {
                return [
                    'status' => 'error',
                    'message' => "HTTP Error: $http_code"
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
$telegram = new TelegramAPI();
$result = $telegram->sendMessage(123456789, "Thank you for your complaint. We are looking into this issue.");
print_r($result);
*/
?>

