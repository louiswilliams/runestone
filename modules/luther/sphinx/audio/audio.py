# Copyright (C) 2013  Bradley N. Miller, Barabara Ericson, Louis Williams
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

__author__ = 'bmiller'

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import Directive

def setup(app):
    app.add_directive('audiotour', AudioTour)
    app.add_stylesheet('codemirror.css')
    app.add_stylesheet('activecode.css')
    app.add_stylesheet('audiotour.css')

    app.add_javascript('jquery.highlight.js' )
    app.add_javascript('bookfuncs.js' )
    app.add_javascript('codemirror.js' )
    app.add_javascript('htmlmixed.js')
    app.add_javascript('clike.js')
    app.add_javascript('activecode.js')
    app.add_javascript('skulpt.min.js' )
    app.add_javascript('skulpt-stdlib.js')

    app.add_node(AudioTourNode, html=(visit_at_node, depart_at_node))

#    app.connect('doctree-resolved',process_activcode_nodes)
#    app.connect('env-purge-doc', purge_activecodes)

START = '''
<div id="cont"></div>
<div id="%(divid)s" lang="%(language)s" class="at_section alert alert-warning" >
'''


EDIT1 = '''
</div>
<br/>
<div id="%(divid)s_code_div" class="at_code_div">
<textarea cols="50" rows="12" id="%(divid)s_code" class="active_code" prefixcode="%(include)s" lang="%(language)s">
%(initialcode)s
</textarea>
</div>
'''

CAPTION = ''' 
<div class="clearfix"></div>
<p class="at_caption"><span class="at_caption_text">%(caption)s</span> </p>
'''

AUDIO = '''
<input type="button" class='btn btn-default ' id="audiob" name="Play Audio" value="Start Audio Tour" onclick="createAudioTourHTML('%(divid)s','%(argu)s','%(no_of_buttons)s','%(ctext)s')"/>
'''

EDIT2 = '''
<div class="at_actions">
'''

SUFF = '''<pre id="%(divid)s_suffix" style="display:none">%(suffix)s</pre>'''

SCRIPT = '''
<script>
if ($("#%(divid)s").attr("lang") !== "html" && $("#%(divid)s_code_div").parents(".admonition").length == 0 && $("#%(divid)s_code_div").parents("#exercises").length == 0){
	if ($(window).width() > 975){
		$("#%(divid)s_code_div").offset({
			left: $("#%(divid)s .clearfix").offset().left
		});
	}
	$("#%(divid)s_runb").one("click", function(){
		$({})
		.queue(function (next) {
			if ($(window).width() > 975){
				$("#%(divid)s_code_div").animate({
					left: 40
				}, 500, next);
			}
			else{
				next();
			}
		})
		.queue(function (next) {
			$("#%(divid)s_runb").parent().siblings(".at_output").show();
			runit('%(divid)s',this, %(include)s);
			$("#%(divid)s_runb").on("click", function(){
				runit('%(divid)s',this, %(include)s);
			});
		})
		
	});
}
else{
	$("#%(divid)s_code_div").css({float : "none", marginLeft : "auto", marginRight : "auto"});
	$("#%(divid)s_runb").parent().siblings(".at_output").show().css({float : "none", right : "0px"});
	$("#%(divid)s_runb").on("click", function(){
		runit('%(divid)s',this, %(include)s);
	});
}
</script>
'''
OUTPUT_START = '''
<div class="at_output">'''

CANVAS = '''
<div style="text-align: center">
<canvas id="%(divid)s_canvas" class="ac-canvas" height="400" width="400" style="border-style: solid; display: none; text-align: center"></canvas>
</div>
'''

OUTPUT_END = '''
</div> <!-- end output -->'''

END = '''
</div>

'''

def visit_at_node(self, node):
    res = START

    if 'tour_1' not in node.at_components:
        res += EDIT2
    else:
        res += EDIT2 + AUDIO

    res += EDIT1
    res += OUTPUT_START

    if 'suffix' in node.at_components:
        res += SUFF

    res += OUTPUT_END
    # res += CAPTION

    res += SCRIPT
    res += END
    res = res % node.at_components
    res = res.replace("u'","'")  # hack:  there must be a better way to include the list and avoid unicode strings

    self.body.append(res)

def depart_at_node(self, node):
	pass

class AudioTourNode(nodes.General, nodes.Element):
    def __init__(self, content):
        """

        Arguments:
        - `self`:
        - `content`:
        """
        super(AudioTourNode, self).__init__()
        self.at_components = content

class AudioTour(Directive):
    required_arguments = 1
    optional_arguments = 1
    has_content = True
    option_spec = {
        'nopre':directives.flag,
        'include':directives.unchanged,
        'caption':directives.unchanged,
        'hidecode':directives.flag,
        'language':directives.unchanged,
        'tour_1':directives.unchanged,
        'tour_2':directives.unchanged,
        'tour_3':directives.unchanged,
        'tour_4':directives.unchanged,
        'tour_5':directives.unchanged
    }

    def run(self):
        env = self.state.document.settings.env

        self.options['divid'] = self.arguments[0]

        # Turn all '====' into newlines
        if self.content:
            if '====' in self.content:
                idx = self.content.index('====')
                source = "\n".join(self.content[:idx])
                suffix = "\n".join(self.content[idx+1:])
            else:
                source = "\n".join(self.content)
                suffix = "\n"
        else:
            source = '\n'
            suffix = '\n'

        if 'caption' not in self.options:
            self.options['caption'] = ''

        if 'language' not in self.options:
            self.options['language'] = 'java'

        complete=""
        no_of_buttons=0
        okeys = self.options.keys()
        for k in okeys:
            if '_' in k:
                x,label = k.split('_')
                no_of_buttons=no_of_buttons+1
                complete=complete+self.options[k]+"*atype*"

        newcomplete=complete.replace("\"","*doubleq*")
        self.options['ctext'] = newcomplete
        self.options['no_of_buttons'] = no_of_buttons

        if 'include' not in self.options:
            self.options['include'] = 'undefined'
        else:
            lst = self.options['include'].split(',')
            lst = [x.strip() for x in lst]
            self.options['include'] = lst

        self.options['initialcode'] = source
        self.options['suffix'] = suffix
        str = source.replace("\n","*nline*")
        str = str.replace("\"","*doubleq*")
        str = str.replace("(","*open*")
        str = str.replace(")","*close*")
        str = str.replace("'","*singleq*")
        self.options['argu']=str

	return [AudioTourNode(self.options)]

if __name__ == '__main__':
    a = AudioTour()

