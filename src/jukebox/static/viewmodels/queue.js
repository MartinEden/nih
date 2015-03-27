function QueueItem(item, info, queue) {
    this.queue = queue;

    this.id  = ko.observable(item.id);
    this.who = ko.observable(item.username);
    this.url = ko.observable(item.url);
    this.secondsToStart = ko.observable(item.timeToStart);

    this.startTime = ko.computed(function() {
        var t = new Date();
        t.setSeconds(t.getSeconds() + this.secondsToStart());
        return t;
    }, this);
    this.timeToStart = ko.computed(function() {
        if (this.secondsToStart()) {
            return moment(this.startTime()).from(new Date());
        } else {
            return "";
        }
    }, this);

    this.metadata = new Metadata(item.url, info);
}

function QueueViewModel(user) {
    this.user = user;
    this.items = ko.observableArray();
    this.busy = false;

    this.count = ko.computed(function() {
        return this.items().length;
    }, this);
}
QueueViewModel.prototype.remove = function(item) {
    this.items.remove(item);
    rpc("dequeue", [this.user.name(), item.id()], updateJukebox);
}
QueueViewModel.prototype.update = function(items, infos) {
    if (!this.busy) {
        this.items.removeAll();
        for (var i = 0; i < items.length; i++) {
            this.items.push(new QueueItem(items[i], infos[i], this));
        }
    }
}
QueueViewModel.prototype.clear = function() {
    this.items.removeAll();
    rpc('clear_queue', [this.user.name()], updateJukebox);
}
QueueViewModel.prototype.setup = function() {
    var me = this;
    // Individual dequeue button
    $("#queue").on("click", "li.item .remove", function(event) {
        var item = ko.dataFor(this);
        item.queue.remove(item);
        event.preventDefault();
    });
    $("#queue .clear-queue").click(function(event) {
        me.clear();
        event.preventDefault();
    });
    // Drag and drop queue re-ordering
    $("#queue ol").sortable({
        revert: true,
        axis: "y",
        start: function(event, ui) {
            me.busy = true;
        },
        stop: function(event, ui) { 
            var item = ko.dataFor(ui.item.get(0));
            // Server indexes from 1, jquery UI from 0
            rpc("reorder", [item.id(), ui.item.index() + 1]);
            me.busy = false;
        },
    });
}
