<?php
class ManageSchedule {
    public static function render_schedule_form() {
        global $wpdb;

        // Days and Time Slots
        $days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'];
        $time_slots = [
            '9:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00',
            '13:00-14:00', '14:00-15:00', '15:00-16:00', '16:00-17:00'
        ];

        // Handle form submission
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['save_schedule'])) {
            $class_id = intval($_POST['class_id']);
            $wpdb->delete("{$wpdb->prefix}class_schedule", ['class_id' => $class_id]);

            foreach ($_POST['schedule'] as $day => $slots) {
                foreach ($slots as $time_slot => $subject) {
                    if (!empty($subject)) {
                        $wpdb->insert(
                            "{$wpdb->prefix}class_schedule",
                            [
                                'class_id' => $class_id,
                                'day' => $day,
                                'time_slot' => $time_slot,
                                'subject' => sanitize_text_field($subject)
                            ]
                        );
                    }
                }
            }

            echo '<p>Schedule saved successfully!</p>';
        }

        // Fetch existing schedule
        $class_id = intval($_GET['class_id'] ?? 0);
        $schedule = [];
        $results = $wpdb->get_results($wpdb->prepare(
            "SELECT day, time_slot, subject FROM {$wpdb->prefix}class_schedule WHERE class_id = %d",
            $class_id
        ));
        foreach ($results as $row) {
            $schedule[$row->day][$row->time_slot] = $row->subject;
        }

        // Render the schedule form
        ?>
        <div class="plugin-form-container">
            <h2>Manage Class Schedule</h2>
            <form method="POST">
                <input type="hidden" name="class_id" value="<?php echo esc_attr($class_id); ?>">

                <table border="1" cellpadding="10" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Time Slot</th>
                            <?php foreach ($days as $day): ?>
                                <th><?php echo esc_html($day); ?></th>
                            <?php endforeach; ?>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($time_slots as $time_slot): ?>
                            <tr>
                                <td><?php echo esc_html($time_slot); ?></td>
                                <?php foreach ($days as $day): ?>
                                    <td>
                                        <input
                                            type="text"
                                            name="schedule[<?php echo esc_attr($day); ?>][<?php echo esc_attr($time_slot); ?>]"
                                            value="<?php echo esc_attr($schedule[$day][$time_slot] ?? ''); ?>"
                                            placeholder="Subject"
                                        >
                                    </td>
                                <?php endforeach; ?>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>

                <button type="submit" name="save_schedule">Save Schedule</button>
            </form>
        </div>
        <?php
    }
}

// Register the shortcode
add_shortcode('manage_schedule', ['ManageSchedule', 'render_schedule_form']);
?>
