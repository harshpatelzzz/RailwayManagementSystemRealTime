<?php
require_once 'config.php';

// Get database connection
$conn = getDBConnection();

// Handle AJAX requests
if (isset($_POST['action'])) {
    header('Content-Type: application/json');
    
    switch ($_POST['action']) {
        case 'get_tweets':
            $filter = isset($_POST['filter']) ? $_POST['filter'] : 'all';
            $query = "SELECT * FROM tweets ORDER BY time DESC LIMIT 100";
            
            if ($filter == 'emergency') {
                $query = "SELECT * FROM tweets WHERE prediction = 1 ORDER BY time DESC LIMIT 100";
            } elseif ($filter == 'feedback') {
                $query = "SELECT * FROM tweets WHERE prediction = 0 ORDER BY time DESC LIMIT 100";
            }
            
            $result = $conn->query($query);
            $tweets = [];
            
            while ($row = $result->fetch_assoc()) {
                $tweets[] = $row;
            }
            
            echo json_encode($tweets);
            exit;
            
        case 'respond_tweet':
            $tweet_id = intval($_POST['tweet_id']);
            $response = mysqli_real_escape_string($conn, $_POST['response']);
            
            // Update response in database
            $update_query = "UPDATE tweets SET response = '$response', response_status = 1 WHERE id = $tweet_id";
            
            if ($conn->query($update_query)) {
                // Post response to Twitter API
                require_once 'twitter_api.php';
                $twitter = new TwitterAPI();
                
                // Get tweet_id from database
                $tweet_query = "SELECT tweet_id FROM tweets WHERE id = $tweet_id";
                $tweet_result = $conn->query($tweet_query);
                if ($tweet_result && $row = $tweet_result->fetch_assoc()) {
                    $original_tweet_id = $row['tweet_id'];
                    if ($original_tweet_id) {
                        $twitter_result = $twitter->replyToTweet($original_tweet_id, $response);
                        if ($twitter_result['status'] === 'error') {
                            echo json_encode(['status' => 'warning', 'message' => 'Response saved but Twitter post failed: ' . $twitter_result['message']]);
                            exit;
                        }
                    }
                }
                
                echo json_encode(['status' => 'success', 'message' => 'Response saved and posted to Twitter']);
            } else {
                echo json_encode(['status' => 'error', 'message' => $conn->error]);
            }
            exit;
            
        case 'get_stats':
            $stats = [];
            
            $total = $conn->query("SELECT COUNT(*) as count FROM tweets")->fetch_assoc()['count'];
            $emergency = $conn->query("SELECT COUNT(*) as count FROM tweets WHERE prediction = 1")->fetch_assoc()['count'];
            $feedback = $conn->query("SELECT COUNT(*) as count FROM tweets WHERE prediction = 0")->fetch_assoc()['count'];
            $responded = $conn->query("SELECT COUNT(*) as count FROM tweets WHERE response_status = 1")->fetch_assoc()['count'];
            
            $stats = [
                'total' => $total,
                'emergency' => $emergency,
                'feedback' => $feedback,
                'responded' => $responded,
                'pending' => $total - $responded
            ];
            
            echo json_encode($stats);
            exit;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?></title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-train"></i> <?php echo APP_NAME; ?>
            </span>
            <div class="d-flex">
                <button class="btn btn-light btn-sm" onclick="refreshData()">
                    <i class="fas fa-sync-alt"></i> Refresh
                </button>
            </div>
        </div>
    </nav>

    <div class="container-fluid mt-4">
        <!-- Statistics Cards -->
        <div class="row mb-4" id="stats-container">
            <div class="col-md-3">
                <div class="card text-white bg-primary">
                    <div class="card-body">
                        <h5 class="card-title">Total Tweets</h5>
                        <h2 id="stat-total">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-danger">
                    <div class="card-body">
                        <h5 class="card-title">Emergency</h5>
                        <h2 id="stat-emergency">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-info">
                    <div class="card-body">
                        <h5 class="card-title">Feedback</h5>
                        <h2 id="stat-feedback">0</h2>
                    </div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="card text-white bg-success">
                    <div class="card-body">
                        <h5 class="card-title">Responded</h5>
                        <h2 id="stat-responded">0</h2>
                    </div>
                </div>
            </div>
        </div>

        <!-- Filter Buttons -->
        <div class="row mb-3">
            <div class="col-12">
                <div class="btn-group" role="group">
                    <button type="button" class="btn btn-outline-primary active" onclick="filterTweets('all')">
                        All Tweets
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="filterTweets('emergency')">
                        Emergency
                    </button>
                    <button type="button" class="btn btn-outline-info" onclick="filterTweets('feedback')">
                        Feedback
                    </button>
                </div>
            </div>
        </div>

        <!-- Tweets Table -->
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">
                        <h5><i class="fas fa-list"></i> Recent Tweets</h5>
                    </div>
                    <div class="card-body">
                        <div class="table-responsive">
                            <table class="table table-hover" id="tweets-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Tweet</th>
                                        <th>Username</th>
                                        <th>PNR</th>
                                        <th>Type</th>
                                        <th>Time</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody id="tweets-tbody">
                                    <tr>
                                        <td colspan="8" class="text-center">Loading tweets...</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Response Modal -->
    <div class="modal fade" id="responseModal" tabindex="-1">
        <div class="modal-dialog">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Respond to Tweet</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label class="form-label">Tweet:</label>
                        <p id="modal-tweet-text" class="border p-2"></p>
                    </div>
                    <div class="mb-3">
                        <label for="response-text" class="form-label">Your Response:</label>
                        <textarea class="form-control" id="response-text" rows="3" maxlength="280"></textarea>
                        <small class="text-muted"><span id="char-count">0</span>/280 characters</small>
                    </div>
                    <input type="hidden" id="modal-tweet-id">
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" onclick="submitResponse()">Send Response</button>
                </div>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.7.0.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script src="../assets/js/main.js"></script>
</body>
</html>

