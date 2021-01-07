<template>
  <div @scroll="showMore" class="container">
    <div class="header">
      <div class="query">
        <div class="keyword">
          <input
            type="text"
            spellcheck="false"
            placeholder='CQL: e.g., "一" [pos="N.*"]{2}'
            v-model.lazy="query.query"
          />
          <button v-on:click="searchDB" id="search">Query</button>

            <div class="info">
              <button @click="exportData" :disabled="isExporting">Export</button>
              <span class="num-of-results">{{ this.results.length }}</span>
          </div>
        </div>
        <ul class="setting">
          <li>
            Left context:
            <input type="number" v-model="query.left" />
          </li>
          <li>
            Right context:
            <input type="number" v-model="query.right" />
          </li>
          <li>
            show tag (keyword):
            <input type="checkbox" v-model="displayOpt.kw.tag" />
          </li>
          <li>
            show tag (context):
            <input type="checkbox" v-model="displayOpt.ctx.tag" />
          </li>
          <li>
            Space b/w tokens:
            <input type="checkbox" v-model="displayOpt.token_sep" />
          </li>
          <li>
            Default token attribute:
            <span class="default_attr" v-if="defaultAttr != null">{{ defaultAttr }}</span>
          </li>
          <li class="this-is-placeholder"></li>
        </ul>
      </div>
    </div>

    <div class="results">
        <div v-if="server_error" class="server_error">
            INVALID CQL SYNTAX
        </div>
      <loading
        loader="spinner"
        :active.sync="query.isLoading"
        :is-full-page="true"
        :can-cancel="true"
      >
        <template v-slot:after>
          <p class="loading-text">Searching . . .</p>
        </template>
        <!-- <slot name="after"></slot> -->
      </loading>
      <div class="kwic" v-bind:key="idx" v-for="(item, idx) in showResults">
        <span class="left" v-bind:style="{ width: kwicStyCtxWidth + '%' }">{{
          item["left"]
            | contextShow(
              (showTag = displayOpt.ctx.tag),
              (defaultAttr = defaultAttr),
              (sep = displayOpt.token_sep ? " ": "")
            )
        }}</span>
        <span class="key" v-bind:style="{ width: kwicStyKeyWidth + '%' }">{{
          item["keyword"]
            | contextShow(
              (showTag = displayOpt.kw.tag),
              (defaultAttr = defaultAttr),
              (sep = displayOpt.token_sep ? " ": "")
            )
        }}</span>
        <span class="right" v-bind:style="{ width: kwicStyCtxWidth + '%' }">{{
          item["right"]
            | contextShow(
              (showTag = displayOpt.ctx.tag),
              (defaultAttr = defaultAttr),
              (sep = displayOpt.token_sep ? " ": "")
            )
        }}</span>
      </div>
      <!-- <button v-on:click="showMore" v-if="results.length > 30">
        Show More
      </button> -->
    </div>

    <a id="to-top" onclick="document.documentElement.scrollTop = 0;">▲</a>
    <a id="to-bottom" onclick="window.scrollTo(0, document.body.scrollHeight);"
      >▼</a
    >
  </div>
</template>

<script>
import VueLoading from "vue-loading-overlay";
import "vue-loading-overlay/dist/vue-loading.css";
import axios from "axios";

export default {
  name: "kwic",
  components: {
    loading: VueLoading,
  },
  data() {
    return {
      query: {
        query: "",
        left: 10,
        right: 10,
        isLoading: false,
      },
      displayOpt: {
        kw: {
          tag: true,
          sep: " ",
        },
        ctx: {
          tag: false,
          sep: " ",
        },
        token_sep: true,
      },
      results: [],
      showNext: {
        curr: 30,
        next: 30,
      },
      //// Options related to server ////
      port: 1420,
      defaultAttr: null,
      server_error: false,
      isExporting: false,
      escapeCharacters: [
        ["{", "___LCURLY_BRACKET___"],
        ["}", "___RCURLY_BRACKET___"],
        ["[", "___LSQUARE_BRACKET___"],
        ["]", "___RSQUARE_BRACKET___"],
        ["\\", "___BACKSLASH___"],
        ["^", "___START_ANCHOR___"],
        [";", "___SEMICOLON___"],
        ["/", "___SLASH___"],
        ["?", "___QUESTION___"],
        [":", "___COLON___"],
        ["@", "___AT___"],
        ["&", "___AMPERSAND___"],
        ["=", "___EQUAL___"],
        ["+", "___PLUS___"],
        ["$", "___END_ANCHOR___"],
        [",", "___COMMA___"],
      ]
      ///////////////////////////////////
    };
  },
  created () {
    window.addEventListener('scroll', this.showMore);
  },
  methods: {
    searchDB: function () {
      var query = this.query.query;
      this.escapeCharacters.forEach(e => {
        query = query.replaceAll(e[0], e[1]);
      })
      console.log(query);
      const url = `http://localhost:${this.port}/query?query=${query}&left=${this.query.left}&right=${this.query.right}`;
      //clean up
      this.showNext.curr = 30;
      this.query.isLoading = true;
      this.$http.get(url).then(
        function (data) {
          this.server_error = false;
          this.results = data.body["results"];
          this.defaultAttr = data.body["default_attr"];
          this.query.isLoading = false;
        },
        (err) => {
          console.log("Err", err);
          this.results = []
          this.query.isLoading = false;
          this.server_error = true;
        }
      );
    },
    showMore: function () {
      if (this.showNext.curr < this.results.length) {
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight)
            this.showNext.curr += this.showNext.next;
      }
    },
    exportData: function () {
      this.isExporting = true;

      const url = `http://localhost:${this.port}/export`;

      axios
        .get(url, { responseType: "blob" })
        .then((response) => {
          const blob = new Blob([response.data], {
            type: "text/tsv",
          });
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = "concordance_list.json";
          link.click();
          URL.revokeObjectURL(link.href);
          // Release button
          this.isExporting = false;
        })
        .catch(console.error);
    },
  },
  computed: {
    showResults() {
      return this.results.slice(0, this.showNext.curr);
    },
    kwicStyKeyWidth() {
      return this.results[0].keyword.length * 6;
    },
    kwicStyCtxWidth() {
      return (95 - this.results[0].keyword.length * 6) / 2;
    },
  },
  filters: {
    contextShow: function (lst, showTag = false, defaultAttr = "word", sep = "\t") {
      const lst2 = [];
      lst.forEach((elem) => {
        if (showTag) {
          const firstValue = elem[defaultAttr];
          var other_values = [];
          Object.entries(elem).forEach(e => {
            if (e[0] != defaultAttr)
              other_values.push(e[1])
          })
          const new_values = [firstValue].concat(other_values);
          lst2.push(new_values.join("/"));
        }
        else lst2.push(elem[defaultAttr]);
      });

      return lst2.join(sep);
    },
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.container {
  height:100%;
  width: 90%;
  margin: 30px auto;
}
.header {
  position: fixed;
  margin: 0;
  padding: 20px 0;
  height: 100px;
  width: 90%;
  min-width: 800px;
  top: 0;
  background: white;
}
.query {
  position: relative;
  display: block;
  width: 100%;
  margin-bottom: 0px;
}
.keyword {
  display: inline-block;
  height: 70px;
  width: 60%;
  margin: 0;
  padding: 0;
  text-align: left;
  vertical-align: top
}
.setting {
  display: inline-block;
  height: 80px;
  width: 40%;
  margin: 0;
  padding: 0;
  list-style-type: none;
}
.keyword input,
.keyword button {
  width: 90%;
  margin: 3px;
  padding: 0.45em;
  font-size: 11px;
  font-family: Monaco, "Courier New", Courier, monospace;
}
.keyword input {
  margin: 0;
}
button#search {
  margin: 5px auto;
  width: 30%;
  padding: 5px;
}
.setting li {
  display: inline-block;
  padding: 5px;
  margin: 3px;
  width: 45%;
  font-size: 12px;
}
.setting input[type="number"] {
  padding: 0;
  width: 2.5em;
}
.setting input[type="text"] {
  padding: 0;
  width: 4.5em;
  text-align: center;
}
.setting .default_attr {
  background: rgba(158, 158, 158, 0.3);
  color: rgb(78, 78, 78);
  padding: 0.2em 0.28em;
  border-radius: 7%;
}
.kwic span {
  display: inline-block;
  width: 40%;
  height: 1.5em;
  /* border: 1px solid black; */
  font-size: 0.78em;
  margin: 3px auto;
  padding: 0.1em;
}
.server_error {
  color: red;
  font-weight: bold;
  font-family: Monaco, monospace;
  font-size: 1.5em;
  text-align: left;
  padding-top: 1.2em;
}
.results .kwic:nth-child(2n + 1) {
  background: rgba(226, 226, 226, 0.9);
}
.results span.key {
  text-align: center;
  color: red;
}
.left {
  text-align: right;
}
.right {
  text-align: left;
}
.results {
  margin-top: 175px;
  counter-reset: num;
}
.kwic::before {
  counter-increment: num;
  content: counter(num) " ";
  color: gray;
  font-size: 0.7em;
}
.loading-text {
  color: rgb(42, 42, 42);
}
.info {
  text-align: left;
}
.info span,
.info button {
  display: inline-block;
  margin: 5px 1.2em 5px 0;
  padding: 6px;
  line-height: 0.75em;
  width: 4.8em;
}
.info span.num-of-results {
  width: 15em;
  font-size: 0.7em;
  /* text-align: left; */
}
.num-of-results:before {
  content: "總筆數：";
}

button {
  background: rgb(87, 87, 87);
  color: rgb(236, 236, 236);
  padding: 4px;
  margin: 5px;
  border: none;
}
button:hover {
  background: rgb(66, 66, 66);
  color: white;
}
button:active {
  transform: translateY(1px);
}
button:disabled {
  background: rgb(136, 136, 136);
  color: rgb(236, 236, 236);
}

a#to-top,
a#to-bottom {
  position: fixed;
  right: 1%;
  background: rgb(121, 121, 121);
  color: rgb(245, 245, 245);
  font-size: 19px;
}
a#to-top:hover,
a#to-bottom:hover {
  background: rgb(88, 88, 88);
  color: white;
  font-size: 20px;
  cursor: pointer;
  user-select: none;
}
a#to-top {
  bottom: 40px;
}
a#to-bottom {
  bottom: 15px;
}
</style>
