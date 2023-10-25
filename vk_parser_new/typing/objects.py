import enum

class GroupsGroupSubject(enum.IntEnum):
    """ GroupsGroupSubject enum """

    auto = 1
    activity_holidays = 2
    business = 3
    pets = 4
    health = 5
    dating_and_communication = 6
    games = 7
    it = 8
    cinema = 9
    beauty_and_fashion = 10
    cooking = 11
    art_and_culture = 12
    literature = 13
    mobile_services_and_internet = 14
    music = 15
    science_and_technology = 16
    real_estate = 17
    news_and_media = 18
    security = 19
    education = 20
    home_and_renovations = 21
    politics = 22
    food = 23
    industry = 24
    travel = 25
    work = 26
    entertainment = 27
    religion = 28
    family = 29
    sports = 30
    insurance = 31
    television = 32
    goods_and_services = 33
    hobbies = 34
    finance = 35
    photo = 36
    esoterics = 37
    electronics_and_appliances = 38
    erotic = 39
    humor = 40
    society_humanities = 41
    design_and_graphics = 42

class GroupsGroupFullSection(enum.IntEnum):
    """ Main section of community """

    none = 0
    photos = 1
    topics = 2
    audios = 3
    videos = 4
    market = 5
    stories = 6
    apps = 7
    followers = 8
    links = 9
    events = 10
    places = 11
    contacts = 12
    app_btns = 13
    docs = 14
    event_counters = 15
    group_messages = 16
    albums = 24
    categories = 26
    admin_help = 27
    app_widget = 31
    public_help = 32
    hs_donation_app = 33
    hs_market_app = 34
    addresses = 35
    artist_page = 36
    podcast = 37
    articles = 39
    admin_tips = 40
    menu = 41
    fixed_post = 42
    chats = 43
    evergreen_notice = 44
    musicians = 45
    narratives = 46
    donut_donate = 47
    clips = 48
    market_cart = 49
    curators = 50
    market_services = 51
    classifieds = 53
    textlives = 54
    donut_for_dons = 55
    badges = 57
    chats_creation = 58

class CodeExceptions(enum.Enum):

    unknown_error = 1
    app_is_offline = 2
    unknown_method = 3
    not_valid_sign = 4
    unsuccessful_auth =5
    too_many_requests_per_second =6 #Задайте больший интервал между вызовами или используйте метод execute.
    # Подробнее об ограничениях на частоту вызовов см. на странице vk.com/dev/api_requests.
    have_not_permission = 7
    not_valid_request = 8
    too_many_same_actions = 9 #Нужно сократить число однотипных обращений. Для более эффективной работы Вы можете использовать execute или JSONP.
    internal_server_error = 10
    in_test_mode_app_must_be_offline = 11
    captcha_required = 14
    access_not_allowed = 15
    https_required = 16
    validation_user_required =17
    page_is_deleted_or_blocked = 18
    this_action_not_allowed_for_standalone_apps = 20
    this_actial_is_allowed_only_for_standalow_or_openapi_apps =21
    method_was_switched_off = 23
    user_confirmation_required = 24
    access_keys_of_group_invalid = 27
    access_keys_of_app_invalid = 28
    reached_limit_on_method_calls = 29
    page_is_private =30
    one_of_required_arguments_of_method_havent_passed = 100
    not_right_api_id_of_app = 101
    invalid_user_id = 113
    invalid_timestamp = 150
    access_to_album_closed = 200
    access_to_audio_closed = 201
    access_to_group_closed = 203
    album_overfilled = 300
    action_not_allowed = 500
    have_not_right_on_actions_with_advrtise_cabinet = 600
    error_with_work_with_advertise_cabinet = 603

