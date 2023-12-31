"use strict";(self.webpackChunk_coreui_coreui_free_react_admin_template=self.webpackChunk_coreui_coreui_free_react_admin_template||[]).push([[758],{12117:(e,s,n)=>{n.d(s,{Z:()=>j});var t=n(72791),r=n(55087),l=n(77618),a=n(22618),o=n(6265),c=n(30734),i=n(45471),d=n(27316),m=n(71987),p=n(95294),h=n(40368),u=n(80184);const x=function(){let e=arguments.length>0&&void 0!==arguments[0]?arguments[0]:{};return{llmConfig:{num_beams:1,do_sample:!0,temperature:1,top_p:1,top_k:50,max_new_tokens:100,repetition_penalty:1,length_penalty:1,...e.llmConfig||{}},requestConfig:{onlyNewTokens:!0,streamResponse:!0,...e.requestConfig||{}}}},j=e=>{let{onChange:s=(()=>{}),showStream:n=!1,defaultConfig:j={},config:g={}}=e;const[b,y]=(0,t.useState)(x(j));(0,t.useEffect)((()=>{v({})}),[]);const _=()=>({...b.llmConfig,...(null===g||void 0===g?void 0:g.llmConfig)||{}}),f=()=>({...b.requestConfig,...(null===g||void 0===g?void 0:g.requestConfig)||{}}),v=e=>{const n={llmConfig:{...b.llmConfig,...e.llmConfig},requestConfig:{...b.requestConfig,...e.requestConfig}};y(n),s(n)},C=e=>{v({llmConfig:e})},k=e=>{v({requestConfig:e})};return(0,u.jsxs)(r.x,{className:"mb-3 ",children:[(0,u.jsxs)(l.b,{children:["Generation Config:",(0,u.jsx)(a.u,{color:"secondary",size:"sm",className:"float-end",onClick:()=>{const e=x(j);y(e),s(e)},children:"reset defaults"})]}),(0,u.jsxs)(o.s,{children:[(0,u.jsx)("small",{children:(0,u.jsx)("br",{})}),(0,u.jsxs)(c.r,{children:[(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Temperature - ",(0,u.jsx)("strong",{children:"\xa0Float"})]}),(0,u.jsx)(p.j,{placeholder:"temperature",type:"number",value:_().temperature,onChange:e=>{const s=parseFloat(e.target.value)||0;C({temperature:s<0?0:s})}})]})}),(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Max new Tokens - ",(0,u.jsx)("strong",{children:"\xa0Int"})]}),(0,u.jsx)(p.j,{placeholder:"max_new_tokens",type:"number",value:_().max_new_tokens,onChange:e=>{const s=parseInt(e.target.value)||0;C({max_new_tokens:s<1?1:s})}})]})})]}),(0,u.jsxs)(c.r,{children:[(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Number of Beams - ",(0,u.jsx)("strong",{children:"\xa0Int"})]}),(0,u.jsx)(p.j,{placeholder:"num_beams",type:"number",value:_().num_beams,onChange:e=>{const s=parseInt(e.target.value)||0;C({num_beams:s<1?1:s})}})]})}),(0,u.jsx)(i.b,{cm:6,children:(0,u.jsx)(d.Y,{className:"mb-3",children:(0,u.jsx)(h.E,{style:{cursor:"pointer"},checked:_().do_sample,onChange:e=>C({do_sample:!!e.target.checked}),className:"mt-2",type:"checkbox",id:"doSample",label:(0,u.jsx)("span",{style:{cursor:"pointer"},children:"Do sample ( Bool )"})})})})]}),(0,u.jsxs)(c.r,{children:[(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Top 'P' - ",(0,u.jsx)("strong",{children:"\xa0Float"})]}),(0,u.jsx)(p.j,{placeholder:"top_p",type:"number",value:_().top_p,onChange:e=>{const s=parseFloat(e.target.value)||0;C({top_p:s<0?0:s})}})]})}),(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Top 'K' - ",(0,u.jsx)("strong",{children:"\xa0Int"})]}),(0,u.jsx)(p.j,{placeholder:"top_k",type:"number",value:_().top_k,onChange:e=>{const s=parseInt(e.target.value)||0;C({top_k:s<0?0:s})}})]})})]}),(0,u.jsxs)(c.r,{children:[(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Repetition penalty - ",(0,u.jsx)("strong",{children:"\xa0Float"})]}),(0,u.jsx)(p.j,{placeholder:"repetition_penalty",type:"number",value:_().repetition_penalty,onChange:e=>{const s=parseFloat(e.target.value)||0;C({repetition_penalty:s<1e-6?1e-6:s})}})]})}),(0,u.jsx)(i.b,{cm:6,children:(0,u.jsxs)(d.Y,{className:"mb-3",children:[(0,u.jsxs)(m.w,{style:{width:205},children:["Length penalty - ",(0,u.jsx)("strong",{children:"\xa0Float"})]}),(0,u.jsx)(p.j,{placeholder:"length_penalty",type:"number",value:_().length_penalty,onChange:e=>{const s=parseFloat(e.target.value)||0;C({length_penalty:s<0?0:s})}})]})})]}),(0,u.jsxs)(c.r,{children:[(0,u.jsx)(i.b,{cm:6,children:(0,u.jsx)(h.E,{style:{cursor:"pointer"},checked:f().onlyNewTokens,onChange:e=>k({onlyNewTokens:e.target.checked}),className:"mt-2",type:"checkbox",id:"onlyNewTokensCheck",label:(0,u.jsx)("span",{style:{cursor:"pointer"},children:"Only return new tokens ( or include prompt )"})})}),(0,u.jsx)(i.b,{cm:6,children:n&&(0,u.jsx)(h.E,{style:{cursor:"pointer"},checked:f().streamResponse,onChange:e=>k({streamResponse:e.target.checked}),className:"mt-2",type:"checkbox",id:"isStreamResponse",label:(0,u.jsx)("span",{style:{cursor:"pointer"},children:"Stream tokens as they are being generated ( or all at once )"})})})]}),(0,u.jsx)("div",{className:"invalid-feedback d-block",children:1!==_().num_beams&&"Multiple beams do not support streaming!"})]})]})}},30218:(e,s,n)=>{n.d(s,{Z:()=>j});var t=n(72791),r=n(6332),l=n(55087),a=n(77618),o=n(30734),c=n(45471),i=n(22618),d=n(6265),m=n(84135),p=n(33906),h=n(50436),u=n(59434),x=n(80184);const j=e=>{let{requestId:s,response:n}=e;const[j,g]=(0,t.useState)(!1),b=(0,u.v9)((e=>{let{theme:s}=e;return"auto"===s?window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light":s})),y={code:e=>{let{node:s,...n}=e;return(0,x.jsx)("span",{children:(0,x.jsx)(m.Z,{language:n.language,style:"dark"===b?p.Z:h.Z,children:n.children})})}};return(0,x.jsxs)(l.x,{className:"mb-5 ",children:[(0,x.jsx)(a.b,{children:(0,x.jsxs)(o.r,{children:[(0,x.jsxs)(c.b,{sm:8,children:[(0,x.jsx)("div",{children:"Response to requestID:"}),(0,x.jsx)("small",{children:s})]}),(0,x.jsx)(c.b,{sm:4,children:(0,x.jsx)(i.u,{size:"sm",color:j?"info":"light",className:"float-end mt-2",onClick:()=>g(!j),children:j?"View markdown":"View raw response"})})]})}),(0,x.jsx)(d.s,{children:j?(0,x.jsx)("span",{className:"markdown-llm",children:n}):(0,x.jsx)(r.U,{components:y,skipHtml:!0,className:"markdown-llm",children:n.replace(/ /g,"\xa0")})})]})}},70009:(e,s,n)=>{n.d(s,{Z:()=>a});n(72791);var t=n(26775),r=n(52424),l=n(80184);const a=e=>{let{responseTimes:s}=e;return(0,l.jsxs)(l.Fragment,{children:[s.length?(0,l.jsx)(t.L,{htmlFor:"exampleFormControlTextarea1",className:"mt-3",children:(0,l.jsx)("strong",{children:"Response time history: "})}):"",(0,l.jsx)("div",{className:"pb-3",style:{overflow:"auto",whiteSpace:"nowrap"},children:s.length?s.map(((e,s)=>(0,l.jsxs)(r.C,{color:"dark",shape:"rounded-pill",className:"me-2",children:[(e/1e3).toFixed(3)," s"]},"badge-".concat(s,"-").concat(e)))):""})]})}},99840:(e,s,n)=>{n.d(s,{Z:()=>l});var t=n(72791),r=n(80184);const l=function(){const[e,s]=(0,t.useState)(0);return(0,t.useEffect)((()=>{const e=(new Date).getTime(),n=setInterval((()=>{s((s=>(new Date).getTime()-e))}),99);return()=>clearInterval(n)}),[]),(0,r.jsx)(r.Fragment,{children:(e/1e3).toFixed(3)})}},34758:(e,s,n)=>{n.r(s),n.d(s,{default:()=>v});var t=n(72791),r=n(48113),l=n(30734),a=n(45471),o=n(55087),c=n(27316),i=n(71987),d=n(95294),m=n(22618),p=n(25512),h=n(26775),u=n(40368),x=n(99840),j=n(54261),g=n(12117),b=n(30218),y=n(70009),_=n(80184);const f="".concat({NODE_ENV:"production",PUBLIC_URL:".",WDS_SOCKET_HOST:void 0,WDS_SOCKET_PATH:void 0,WDS_SOCKET_PORT:void 0,FAST_REFRESH:!0}.REACT_APP_BASE_URL||"","/api/generate-batch");const v=()=>{const[e,s]=(0,t.useState)([{prompt:"[INST] Generate a very long poem about 1000 cats [/INST]\n\n",requestId:(0,j.Z)(),id:(0,j.Z)()},{prompt:"[INST] Generate a very short poem about 1000 dogs [/INST]\n\n",requestId:(0,j.Z)(),id:(0,j.Z)()}]),[n,v]=(0,t.useState)(!1),[C,k]=(0,t.useState)(!1),[w,N]=(0,t.useState)([]),[S,T]=(0,t.useState)(null),[I,q]=(0,t.useState)(0),[E,F]=(0,t.useState)([]),[Z,R]=(0,t.useState)(0),[A,D]=(0,t.useState)(""),[O,P]=(0,t.useState)(!1),[Y,L]=(0,t.useState)(!1),[G,B]=(0,t.useState)({}),[H,K]=(0,t.useState)(0);(0,t.useEffect)((()=>{!C||!Y||O||n||Z?v(!1):U()}),[H]);const U=async()=>{P(!0),v(!1),D(""),R(0),q(0);let s=e.map((e=>{let{requestId:s}=e;return{request_id:s,response:""}}));var n;Y?null!==G&&void 0!==G&&null!==(n=G.requestConfig)&&void 0!==n&&n.onlyNewTokens&&(s=[...w]):(F([]),N([]));try{var t;const{responseTime:n,response:r,json:l}=await async function(e,s){let n=arguments.length>2&&void 0!==arguments[2]?arguments[2]:()=>{};const t=(new Date).getTime(),r=new AbortController,l=r.signal;n(r);const a=await fetch(e,{method:"POST",body:JSON.stringify(s),signal:l});return{json:200===a.status||206===a.status?await a.json():await a.text(),response:a,responseTime:(new Date).getTime()-t}}(f,{prompts:e.map((e=>{let{requestId:s,prompt:n}=e;return{request_id:s,prompt:n}})),only_new_tokens:!(null===G||void 0===G||null===(t=G.requestConfig)||void 0===t||!t.onlyNewTokens),generation_config:G.llmConfig},(e=>{T(e)}));if(200===r.status||206===r.status){N(l.map(((e,n)=>{const t=s.find((s=>{let{request_id:n}=s;return n===e.request_id}))||{response:""};return{...e,response:t.response+=(e.prompt||"")+e.response}}))),F(Y?[...E,n]:[n]),q(n),K(H+1);const e=200===r.status;L(!e),e&&v(!1)}else R(1),D(l)}catch(r){"AbortError"===r.name?R(2):(console.error(r),R(1),D(r.message)),T(null),P(!1),v(!1)}finally{T(null),P(!1)}},W=(n,t)=>{const r=e.findIndex((e=>e.id===n));e[r]={...e[r],...t},s([...e])};return(0,_.jsxs)(_.Fragment,{children:[(0,_.jsxs)(r.l,{className:"pb-5",children:[(0,_.jsx)(g.Z,{config:G,onChange:e=>B(e),showStream:!0}),(0,_.jsx)(l.r,{children:e.map(((n,t)=>{let{prompt:r,requestId:l,id:h}=n;return(0,_.jsx)(a.b,{sm:6,className:"mt-4",children:(0,_.jsxs)(o.x,{children:[(0,_.jsxs)(c.Y,{children:[(0,_.jsx)(i.w,{children:"RequestId"}),(0,_.jsx)(d.j,{disabled:O||Y,placeholder:"requestId",type:"text",value:l,onChange:e=>W(h,{requestId:e.target.value})}),t>1&&(0,_.jsx)(m.u,{disabled:Y,color:"danger",onClick:()=>(n=>{const t=e.findIndex((e=>e.id===n));e.splice(t,1),s([...e])})(h),children:(0,_.jsx)("strong",{children:"Clear"})})]}),(0,_.jsx)(p.P,{placeholder:"[INST] Generate a very long poem about 1000 cats [/INST]\\n\\n",disabled:O||Y,value:r,invalid:!!Z||!r,onChange:e=>W(h,{prompt:e.target.value}),id:"exampleFormControlTextarea1",rows:10})]})},"batch-prompt-".concat(h))}))}),!!Z&&(0,_.jsx)("div",{className:"invalid-feedback d-block mt-0",children:2===Z?"Aborting might cause some data to be lost, its best to reset after aborting!":A||"Error generating a response, check your console"}),(0,_.jsx)(y.Z,{responseTimes:E}),(0,_.jsxs)("div",{className:"mb-3 ",children:[(0,_.jsxs)(m.u,{color:"primary",disabled:O||Y,onClick:()=>{s([...e,{requestId:(0,j.Z)(),prompt:"",id:(0,j.Z)()}])},children:[" ","+"," "]}),(0,_.jsx)(m.u,{className:"ms-3",color:"primary",disabled:O||!e.every((e=>{let{prompt:s}=e;return!!s})),onClick:()=>U(),children:n&&O?"Stopping...":O?"Waiting...":Y?"Continue":"Send Prompt"}),Y&&!O&&" or ",!O&&Y&&(0,_.jsx)(m.u,{color:"secondary",disabled:O,onClick:()=>{v(!1),N([]),s(e.map((e=>({...e,requestId:(0,j.Z)()})))),T(null),q(0),F([]),R(0),D(""),P(!1),L(!1)},children:"reset"}),O?(0,_.jsxs)(h.L,{children:[(0,_.jsx)("strong",{children:"\xa0\xa0Segment time:\xa0"}),(0,_.jsx)(x.Z,{})," seconds"]}):I?(0,_.jsxs)(h.L,{children:[(0,_.jsx)("strong",{children:"\xa0\xa0Generation:\xa0"}),E.reduce(((e,s)=>e+s),0)/1e3," seconds"]}):"",(0,_.jsx)(m.u,{color:"secondary",className:"float-end ms-3",disabled:!C,onClick:()=>v(!0),children:"Stop"}),(0,_.jsx)(m.u,{color:"secondary",className:"float-end",disabled:!O,onClick:()=>{v(!0),S&&S.abort()},children:"Abort"}),"\xa0\xa0"]}),(0,_.jsx)(u.E,{style:{cursor:"pointer"},checked:C,disabled:O,onChange:e=>k(e.target.checked),className:"mt-2",type:"checkbox",id:"autoContinueCheck",label:(0,_.jsx)("span",{style:{cursor:"pointer"},children:"Automatically continue prompt generation when didnt reach EOS"})})]}),(0,_.jsx)(l.r,{children:w.map((e=>{let{request_id:s,response:n}=e;return(0,_.jsx)(a.b,{sm:6,className:"mt-4",children:(0,_.jsx)(b.Z,{requestId:s,response:n},s)},"batch-prompt-".concat(s))}))})]})}},48113:(e,s,n)=>{n.d(s,{l:()=>c});var t=n(83229),r=n(72791),l=n(52007),a=n.n(l),o=n(64379),c=(0,r.forwardRef)((function(e,s){var n=e.children,l=e.className,a=e.validated,c=(0,t._T)(e,["children","className","validated"]);return r.createElement("form",(0,t.pi)({className:(0,o.Z)({"was-validated":a},l)||void 0},c,{ref:s}),n)}));c.propTypes={children:a().node,className:a().string,validated:a().bool},c.displayName="CForm"}}]);
//# sourceMappingURL=758.a54a6f5f.chunk.js.map