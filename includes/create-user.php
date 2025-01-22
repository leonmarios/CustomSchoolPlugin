<?php
class CreateUser {
    public static function create_user_form() {
        global $wpdb;

        // Form submission handling
        if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['create_user'])) {
            $data = [
                'name' => sanitize_text_field($_POST['name']),
                'email' => sanitize_email($_POST['email']),
                'class_id' => intval($_POST['class_id']),
            ];

            $wpdb->insert($wpdb->prefix . 'users', $data);
            echo '<p>User created successfully!</p>';
        }

        // Fetch classes for dropdown
        $classes = $wpdb->get_results("SELECT id, name FROM {$wpdb->prefix}classes");

        // Render the form
        ?>
    <div id="user-form">
        <ul class="tabs">
            <li><a href="#section1">Κοινωνικό Ιστορικό</a></li>
            <li><a href="#section2">Δημογραφικά Στοιχεία</a></li>
            <li><a href="#section3">Γνωματεύσεις Ειδικών</a></li>
            <li><a href="#section4">Οικογενειακή Κατάσταση</a></li>
            <li><a href="#section5">Ψυχοκινητική Εξέλιξη - Υγεία</a></li>
            <li><a href="#section6">Εκπαίδευση</a></li>
            <li><a href="#section7">Σχολικές Κατακτήσεις</a></li>
            <li><a href="#section8">Δεξιότητες - Συμπεριφορά</a></li>
            <li><a href="#section9">Λοιπά Στοιχεία</a></li>
            <li><a href="#section10">Επίδομα - Σύνταξη</a></li>
            <li><a href="#section11">Σχόλια - Παρατηρήσεις</a></li>
        </ul>

        <form method="POST" enctype="multipart/form-data">
            <!-- Section 1: Κοινωνικό Ιστορικό -->
            <div id="section1" class="tab-content">
                <label>Φάκελος: Ονοματεπώνυμο:</label>
                <input type="text" name="file_name" required>
                <label>Ημερομηνία Προσέλευσης:</label>
                <input type="date" name="arrival_date">
                <label>RV Διεπιστημονική Ομάδα:</label>
                <input type="text" name="rv_team">
                <label>Ανακοίνωση Απόφασης:</label>
                <input type="text" name="decision_announcement">
                <label>Τμήμα:</label>
                <select name="class">
                    <option value="">-- Επιλέξτε Τμήμα --</option>
                    <!-- Populate dynamically from database -->
                </select>
                <label>Ημερομηνία Αποχώρησης:</label>
                <input type="date" name="departure_date">
            </div>

            <!-- Section 2: Δημογραφικά Στοιχεία -->
            <div id="section2" class="tab-content">
                <label>Φωτογραφία:</label>
                <input type="file" name="photo">
                <label>Όνομα:</label>
                <input type="text" name="first_name" required>
                <label>Επώνυμο:</label>
                <input type="text" name="last_name" required>
                <label>Όνομα Πατρός:</label>
                <input type="text" name="father_first_name">
                <label>Επώνυμο Πατρός:</label>
                <input type="text" name="father_last_name">
                <label>Όνομα Μητρός:</label>
                <input type="text" name="mother_first_name">
                <label>Επώνυμο Μητρός:</label>
                <input type="text" name="mother_last_name">
                <label>Όνομα Αδερφού/ης 1:</label>
                <input type="text" name="sibling1_name">
                <label>Όνομα Αδερφού/ης 2:</label>
                <input type="text" name="sibling2_name">
                <label>Όνομα Αδερφού/ης 3:</label>
                <input type="text" name="sibling3_name">
                <label>Όνομα Δικαστικού Συμπαραστάτη:</label>
                <input type="text" name="guardian_first_name">
                <label>Επώνυμο Δικαστικού Συμπαραστάτη:</label>
                <input type="text" name="guardian_last_name">
                <label>Ημερομηνία Γέννησης:</label>
                <input type="date" name="birth_date">
                <label>Ηλικία:</label>
                <input type="number" name="age">
                <label>Τόπος Γέννησης:</label>
                <input type="text" name="birth_place">
                <label>Οικογενειακή Κατάσταση Δ.Σ.:</label>
                <input type="radio" name="family_status_ds" value="Άγαμος"> Άγαμος
                <input type="radio" name="family_status_ds" value="Έγγαμος"> Έγγαμος
                <input type="radio" name="family_status_ds" value="Διαζευγμένος"> Διαζευγμένος
                <label>Οικογενειακή Κατάσταση Συμπαραστάτη:</label>
                <input type="radio" name="family_status_guardian" value="Άγαμος"> Άγαμος
                <input type="radio" name="family_status_guardian" value="Έγγαμος"> Έγγαμος
                <input type="radio" name="family_status_guardian" value="Διαζευγμένος"> Διαζευγμένος
                <label>Διεύθυνση:</label>
                <input type="text" name="address">
                <label>Τηλέφωνο Ωφελούμενου:</label>
                <input type="text" name="phone">
                <label>ΤΗΛ. Δ.Σ./ΕΚΤΑΚΤΗΣ ΑΝΑΓΚΗΣ:</label>
                <input type="text" name="emergency_contact">
                <label>Email ωφελούμενου:</label>
                <input type="email" name="email">
                <label>Email δικαστικού συμπαραστάτη:</label>
                <input type="email" name="guardian_email">
                <label>Email δικαστικού συμπαραστάτη 2:</label>
                <input type="email" name="guardian_email2">
                <label>Α.Δ.Τ. ωφελούμενου:</label>
                <input type="text" name="id_number">
                <label>ΑΜΚΑ Ωφελούμενου:</label>
                <input type="number" name="amka">
                <label>Τρόπος ασφάλισης:</label>
                <input type="radio" name="insurance_type" value="Άμεσα Ασφαλισμένος"> Άμεσα Ασφαλισμένος
                <input type="radio" name="insurance_type" value="Έμμεσα Ασφαλισμένος"> Έμμεσα Ασφαλισμένος
                <label>Ασφαλιστικό Ταμείο:</label>
                <input type="text" name="insurance_fund">
                <label>ΑΜΑ Ωφελούμενου:</label>
                <input type="text" name="ama">
                <label>ΑΜΑ Αμεσα Ασφαλισμένου:</label>
                <input type="text" name="ama_direct">
                <label>ΑΦΜ:</label>
                <input type="number" name="afm">
                <label>Δικαστική Συμπαράσταση:</label>
                <input type="text" name="legal_support">
                <label>Απόφαση Δικαστηρίου:</label>
                <input type="text" name="court_decision">
                <label>Συμφωνία Ένταξης:</label>
                <input type="text" name="integration_agreement">
                <label>GDPR:</label>
                <input type="text" name="gdpr">
                <label>Παραπομπή:</label>
                <input type="text" name="referral">
                <label>Άλλη πληροφορία:</label>
                <input type="text" name="other_info">
            </div>

            <!-- Section 3: Γνωματεύσεις Ειδικών -->
            <div id="section3" class="tab-content">
                <label>ΚΕΣΥ:</label>
                <input type="radio" name="kesy" value="Ναι"> Ναι
                <input type="radio" name="kesy" value="Όχι"> Όχι
                <label>ΚΕΠΑ:</label>
                <input type="radio" name="kepa" value="Ναι"> Ναι
                <input type="radio" name="kepa" value="Όχι"> Όχι
                <label>Άλλες Γνωματεύσεις:</label>
                <input type="text" name="other_diagnoses">
            </div>

            <!-- Section 4: Οικογενειακή Κατάσταση -->
<div id="section4" class="tab-content">
    <!-- Member 1 -->
    <label>Όνομα 1ου μέλους:</label>
    <input type="text" name="family_member1_name">
    <label>Επώνυμο 1ου μέλους:</label>
    <input type="text" name="family_member1_lastname">
    <label>Συγγενική σχέση 1ου μέλους:</label>
    <input type="text" name="family_member1_relationship">
    <label>Ημερομηνία γέννησης 1ου μέλους:</label>
    <input type="date" name="family_member1_birthdate">
    <label>Εκπαίδευση 1ου μέλους:</label>
    <input type="text" name="family_member1_education">
    <label>Επάγγελμα 1ου μέλους:</label>
    <input type="text" name="family_member1_profession">
    <label>Κατάσταση υγείας 1ου μέλους:</label>
    <input type="text" name="family_member1_health">

    <!-- Member 2 -->
    <label>Όνομα 2ου μέλους:</label>
    <input type="text" name="family_member2_name">
    <label>Επώνυμο 2ου μέλους:</label>
    <input type="text" name="family_member2_lastname">
    <label>Συγγενική σχέση 2ου μέλους:</label>
    <input type="text" name="family_member2_relationship">
    <label>Ημερομηνία γέννησης 2ου μέλους:</label>
    <input type="date" name="family_member2_birthdate">
    <label>Εκπαίδευση 2ου μέλους:</label>
    <input type="text" name="family_member2_education">
    <label>Επάγγελμα 2ου μέλους:</label>
    <input type="text" name="family_member2_profession">
    <label>Κατάσταση υγείας 2ου μέλους:</label>
    <input type="text" name="family_member2_health">

    <!-- Member 3 -->
    <label>Όνομα 3ου μέλους:</label>
    <input type="text" name="family_member3_name">
    <label>Επώνυμο 3ου μέλους:</label>
    <input type="text" name="family_member3_lastname">
    <label>Συγγενική σχέση 3ου μέλους:</label>
    <input type="text" name="family_member3_relationship">
    <label>Ημερομηνία γέννησης 3ου μέλους:</label>
    <input type="date" name="family_member3_birthdate">
    <label>Εκπαίδευση 3ου μέλους:</label>
    <input type="text" name="family_member3_education">
    <label>Επάγγελμα 3ου μέλους:</label>
    <input type="text" name="family_member3_profession">
    <label>Κατάσταση υγείας 3ου μέλους:</label>
    <input type="text" name="family_member3_health">

    <!-- Member 4 -->
    <label>Όνομα 4ου μέλους:</label>
    <input type="text" name="family_member4_name">
    <label>Επώνυμο 4ου μέλους:</label>
    <input type="text" name="family_member4_lastname">
    <label>Συγγενική σχέση 4ου μέλους:</label>
    <input type="text" name="family_member4_relationship">
    <label>Ημερομηνία γέννησης 4ου μέλους:</label>
    <input type="date" name="family_member4_birthdate">
    <label>Εκπαίδευση 4ου μέλους:</label>
    <input type="text" name="family_member4_education">
    <label>Επάγγελμα 4ου μέλους:</label>
    <input type="text" name="family_member4_profession">
    <label>Κατάσταση υγείας 4ου μέλους:</label>
    <input type="text" name="family_member4_health">

    <!-- Member 5 -->
    <label>Όνομα 5ου μέλους:</label>
    <input type="text" name="family_member5_name">
    <label>Επώνυμο 5ου μέλους:</label>
    <input type="text" name="family_member5_lastname">
    <label>Συγγενική σχέση 5ου μέλους:</label>
    <input type="text" name="family_member5_relationship">
    <label>Ημερομηνία γέννησης 5ου μέλους:</label>
    <input type="date" name="family_member5_birthdate">
    <label>Εκπαίδευση 5ου μέλους:</label>
    <input type="text" name="family_member5_education">
    <label>Επάγγελμα 5ου μέλους:</label>
    <input type="text" name="family_member5_profession">
    <label>Κατάσταση υγείας 5ου μέλους:</label>
    <input type="text" name="family_member5_health">

    <!-- Member 6 -->
    <label>Όνομα 6ου μέλους:</label>
    <input type="text" name="family_member6_name">
    <label>Επώνυμο 6ου μέλους:</label>
    <input type="text" name="family_member6_lastname">
    <label>Συγγενική σχέση 6ου μέλους:</label>
    <input type="text" name="family_member6_relationship">
    <label>Ημερομηνία γέννησης 6ου μέλους:</label>
    <input type="date" name="family_member6_birthdate">
    <label>Εκπαίδευση 6ου μέλους:</label>
    <input type="text" name="family_member6_education">
    <label>Επάγγελμα 6ου μέλους:</label>
    <input type="text" name="family_member6_profession">
    <label>Κατάσταση υγείας 6ου μέλους:</label>
    <input type="text" name="family_member6_health">
</div>

<!-- Section 5: Ψυχοκινητική Εξέλιξη - Υγεία -->
<div id="section5" class="tab-content">
    <label>Κινητική Ανάπτυξη (Βάδισε ελεύθερα):</label>
    <input type="text" name="motor_development">
    <label>Ομιλία - Πρώτες λέξεις:</label>
    <input type="text" name="speech_first_words">
    <label>Ομιλία - Σχηματισμός προτάσεων:</label>
    <input type="text" name="speech_sentence_form">
    <label>Επικοινωνία:</label>
    <input type="text" name="communication">
    <label>Έλεγχος σφιγκτήρων:</label>
    <input type="text" name="sphincter_control">
    <label>Έμμηνος ρήση:</label>
    <input type="text" name="menstruation">
    <label>Αλλεργίες:</label>
    <input type="text" name="allergies">
    <label>Σεξουαλική Διαπαιδαγώγηση:</label>
    <input type="text" name="sexual_education">
    <label>Κρίσεις Επιληψίας:</label>
    <input type="text" name="epilepsy">
    <label>Άλλα προβλήματα:</label>
    <input type="text" name="other_health_issues">
    <label>Φαρμακευτική αγωγή:</label>
    <input type="text" name="medication">
    <label>Γιατρός:</label>
    <input type="text" name="doctor">
</div>

<!-- Section 6: Εκπαίδευση -->
<div id="section6" class="tab-content">
    <label>Προσχολική Αγωγή:</label>
    <input type="text" name="preschool_education">
    <label>Δημοτικό:</label>
    <input type="text" name="primary_education">
    <label>Γυμνάσιο:</label>
    <input type="text" name="secondary_education">
    <label>Λύκειο:</label>
    <input type="text" name="highschool_education">
    <label>Σχολείο Ειδικής Αγωγής:</label>
    <input type="text" name="special_education_school">
    <label>Εργαστήριο Ειδικής Αγωγής:</label>
    <input type="text" name="special_education_lab">
    <label>Άλλο:</label>
    <input type="text" name="other_education_programs">
</div>

<!-- Section 7: Σχολικές Κατακτήσεις -->
<div id="section7" class="tab-content">
    <label>Ανάγνωση:</label>
    <input type="text" name="reading">
    <label>Γραφή:</label>
    <input type="text" name="writing">
    <label>Αριθμητική:</label>
    <input type="text" name="arithmetic">
    <label>Χρήματα:</label>
    <input type="text" name="money_handling">
    <label>Ώρα:</label>
    <input type="text" name="time_reading">
</div>

<!-- Section 8: Δεξιότητες - Συμπεριφορά -->
<div id="section8" class="tab-content">
    <label>Ντύσιμο-γδύσιμο:</label>
    <input type="text" name="dressing">
    <label>Φαγητό:</label>
    <input type="text" name="eating">
    <label>Ατομική καθαριότητα:</label>
    <input type="text" name="personal_hygiene">
    <label>Τουαλέτα:</label>
    <input type="text" name="toilet_use">
    <label>Συμμετοχή στις δουλειές του σπιτιού:</label>
    <input type="text" name="household_tasks">
    <label>Κυκλοφορία – ψώνια:</label>
    <input type="text" name="shopping">
    <label>Συμπεριφορά/σχέσεις με τους άλλους:</label>
    <input type="text" name="relationships">
    <label>Συντροφικές/Σεξουαλικές Σχέσεις:</label>
    <input type="text" name="intimate_relationships">
    <label>Ελεύθερος χρόνος:</label>
    <input type="text" name="free_time_activities">
    <label>Άλλες πληροφορίες:</label>
    <input type="text" name="other_skills_info">
</div>

<!-- Section 9: Λοιπά Στοιχεία -->
<div id="section9" class="tab-content">
    <label>Απόφαση ΚΕΠΑ:</label>
    <input type="text" name="decision_kepa">
    <label>Ιατρικές Γνωματεύσεις ΕΟΠΥΥ:</label>
    <input type="text" name="medical_opinions">
    <label>Λήξη Γνωματεύσεων ΕΟΠΥΥ:</label>
    <input type="text" name="medical_opinions_expiry">
    <label>Ασφαλιστική ικανότητα:</label>
    <input type="text" name="insurance_eligibility">
    <label>Λήξη Ασφαλιστικής ικανότητας:</label>
    <input type="text" name="insurance_expiry">
</div>

<!-- Section 10: Επίδομα - Σύνταξη -->
<div id="section10" class="tab-content">
    <label>Προνοιακό επίδομα με ποσοστό αναπηρίας:</label>
    <input type="radio" name="disability_benefit" value="Όχι"> Όχι
    <input type="radio" name="disability_benefit" value="67%"> 67%
    <input type="radio" name="disability_benefit" value="80%"> 80%
    <input type="text" name="disability_benefit_other">
    <label>Σύνταξη ασφαλισμένου συνταξιούχου γονέα:</label>
    <input type="radio" name="parent_pension" value="Ναι"> Ναι
    <input type="radio" name="parent_pension" value="Όχι"> Όχι
</div>

<!-- Section 11: Σχόλια - Παρατηρήσεις -->
<div id="section11" class="tab-content">
    <label>Σχόλια - Παρατηρήσεις:</label>
    <input type="text" name="comments">
    <label>Κοινωνικός λειτουργός:</label>
    <input type="text" name="social_worker">
    <label>Διεπιστημονική Ομάδα:</label>
    <input type="text" name="interdisciplinary_team">
</div>


            <button type="submit" name="create_user">Create User</button>
        </form>
    </div>

    <style>
        .tabs { display: flex; list-style-type: none; }
        .tabs li { margin-right: 10px; }
        .tabs a { text-decoration: none; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
    </style>

    <script>
        document.querySelectorAll('.tabs a').forEach(tab => {
            tab.addEventListener('click', function(e) {
                e.preventDefault();
                document.querySelectorAll('.tab-content').forEach(section => section.classList.remove('active'));
                document.querySelector(this.getAttribute('href')).classList.add('active');
            });
        });
    </script>
   
 <?php
}
}
add_shortcode('create_user_form', 'create_user_form');
?>

