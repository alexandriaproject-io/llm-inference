"use strict";(self.webpackChunk_coreui_coreui_free_react_admin_template=self.webpackChunk_coreui_coreui_free_react_admin_template||[]).push([[184],{22184:(e,s,t)=>{t.r(s),t.d(s,{default:()=>T});var n=t(72791),a=t(48113),r=t(55087),l=t(77618),o=t(6265),c=t(30734),i=t(45471),d=t(27316),m=t(71987),h=t(95294),p=t(40368),u=t(26775),x=t(25512),j=t(2328),g=t(52424),b=t(22618),y=t(80184);const _=function(){const[e,s]=(0,n.useState)(0);return(0,n.useEffect)((()=>{const e=(new Date).getTime(),t=setInterval((()=>{s((s=>(new Date).getTime()-e))}),99);return()=>clearInterval(t)}),[]),(0,y.jsx)(y.Fragment,{children:e/1e3})};var k=t(54261),w=t(6332),v=t(84135),N=t(92510),S=t(63564),C=t(59434);const f="".concat("","/api/generate-one");const T=()=>{const[e,s]=(0,n.useState)((0,k.Z)()),[t,T]=(0,n.useState)("[INST] Generate a very long poem about 1000 cats [/INST]\n\n"),[I,F]=(0,n.useState)(!1),[E,D]=(0,n.useState)(!1),[Y,A]=(0,n.useState)(!0),[Z,G]=(0,n.useState)(""),[L,O]=(0,n.useState)(null),[P,R]=(0,n.useState)(0),[q,M]=(0,n.useState)([]),[W,B]=(0,n.useState)(0),[V,H]=(0,n.useState)(!1),[J,K]=(0,n.useState)(!1),[U,z]=(0,n.useState)(!1),[Q,X]=(0,n.useState)(!1),[$,ee]=(0,n.useState)({num_beams:1,do_sample:!1,temperature:1,top_p:1,top_k:50,max_new_tokens:100,repetition_penalty:1,length_penalty:1}),se=(0,C.v9)((e=>{let{theme:s}=e;return"auto"===s?window.matchMedia("(prefers-color-scheme: dark)").matches?"dark":"light":s})),te={code:e=>{let{node:s,...t}=e;return(0,y.jsx)("span",{children:(0,y.jsx)(v.Z,{language:t.language,style:"dark"===se?S.Z:N.Z,children:t.children})})}};(0,n.useEffect)((()=>{!E||!Q||J||V||I||W?F(!1):ne()}),[P]);const ne=async()=>{H(!0),K(!1),F(!1),B(0),R(0);let s="";Q?s=Y?Z:"":M([]);try{const{responseTime:n,response:a}=await async function(e,s){let t=arguments.length>2&&void 0!==arguments[2]?arguments[2]:()=>{},n=arguments.length>3&&void 0!==arguments[3]?arguments[3]:()=>{};const a=(new Date).getTime(),r=new AbortController,l=r.signal,o=await fetch(e,{method:"POST",body:JSON.stringify(s),signal:l});n(r);const c=o.body.getReader();for(;;){const{done:e,value:s}=await c.read();if(e)break;t((new TextDecoder).decode(s))}return{response:o,responseTime:(new Date).getTime()-a}}(f,{request_id:e,prompt:t,only_new_tokens:Y,generation_config:$},(e=>{s+=e,H(!1),K(!0),G(s)}),(e=>O(e)));200!==a.status?B(1):M(Q?[...q,n]:[n]),R(n)}catch(n){"AbortError"===n.name?(console.log("Aborting"),B(2)):(console.error(n),B(1)),O(null),H(!1),K(!1),F(!1)}finally{O(null),H(!1),K(!1);const e=s.trimEnd().endsWith("</s>");X(!e),e&&F(!1)}};return(0,y.jsxs)(y.Fragment,{children:[(0,y.jsxs)(a.l,{className:"pb-3",children:[(0,y.jsxs)(r.x,{className:"mb-3 ",children:[(0,y.jsx)(l.b,{children:"Generation Config:"}),(0,y.jsxs)(o.s,{children:[(0,y.jsx)("small",{children:(0,y.jsx)("br",{})}),(0,y.jsxs)(c.r,{children:[(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Temperature - ",(0,y.jsx)("strong",{children:"\xa0Float"})]}),(0,y.jsx)(h.j,{placeholder:"temperature",type:"number",value:$.temperature<0?0:$.temperature,onChange:e=>ee({...$,temperature:parseFloat(e.target.value)||0})})]})}),(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Max new Tokens - ",(0,y.jsx)("strong",{children:"\xa0Int"})]}),(0,y.jsx)(h.j,{placeholder:"max_new_tokens",type:"number",value:$.max_new_tokens<0?0:$.max_new_tokens,onChange:e=>ee({...$,max_new_tokens:parseInt(e.target.value)||0})})]})})]}),(0,y.jsxs)(c.r,{children:[(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Number of Beams - ",(0,y.jsx)("strong",{children:"\xa0Int"})]}),(0,y.jsx)(h.j,{placeholder:"num_beams",type:"number",value:$.num_beams<1?1:$.num_beams,onChange:e=>ee({...$,num_beams:parseInt(e.target.value)||0})})]})}),(0,y.jsx)(i.b,{cm:6,children:(0,y.jsx)(d.Y,{className:"mb-3",children:(0,y.jsx)(p.E,{style:{cursor:"pointer"},checked:$.do_sample,onChange:e=>ee({...$,do_sample:e.target.checked}),className:"mt-2",type:"checkbox",id:"doSample",label:(0,y.jsx)("span",{style:{cursor:"pointer"},children:"Do sample ( Bool )"})})})})]}),(0,y.jsxs)(c.r,{children:[(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Top 'P' - ",(0,y.jsx)("strong",{children:"\xa0Float"})]}),(0,y.jsx)(h.j,{placeholder:"top_p",type:"number",value:$.top_p<0?0:$.top_p,onChange:e=>ee({...$,top_p:parseFloat(e.target.value)||0})})]})}),(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Top 'K' - ",(0,y.jsx)("strong",{children:"\xa0Int"})]}),(0,y.jsx)(h.j,{placeholder:"top_k",type:"number",value:$.top_k<0?0:$.top_k,onChange:e=>ee({...$,top_k:parseInt(e.target.value)||0})})]})})]}),(0,y.jsxs)(c.r,{children:[(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Repetition penalty - ",(0,y.jsx)("strong",{children:"\xa0Float"})]}),(0,y.jsx)(h.j,{placeholder:"repetition_penalty",type:"number",value:$.repetition_penalty<0?0:$.repetition_penalty,onChange:e=>ee({...$,repetition_penalty:parseFloat(e.target.value)||0})})]})}),(0,y.jsx)(i.b,{cm:6,children:(0,y.jsxs)(d.Y,{className:"mb-3",children:[(0,y.jsxs)(m.w,{style:{width:205},children:["Length penalty - ",(0,y.jsx)("strong",{children:"\xa0Float"})]}),(0,y.jsx)(h.j,{placeholder:"length_penalty",type:"number",value:$.length_penalty<0?0:$.length_penalty,onChange:e=>ee({...$,length_penalty:parseFloat(e.target.value)||0})})]})})]}),(0,y.jsx)("div",{className:"invalid-feedback d-block",children:1!==$.num_beams&&"Multiple beams do not support streaming!"})]})]}),(0,y.jsxs)("div",{className:"mb-3",children:[(0,y.jsxs)(u.L,{htmlFor:"exampleFormControlTextarea1",children:[(0,y.jsx)("strong",{children:"Write your prompt "}),"- ",(0,y.jsxs)("small",{children:["RequestID: ",e]})]}),(0,y.jsx)(x.P,{placeholder:"[INST] Generate a very long poem about 1000 cats [/INST]\\n\\n",disabled:V||J||Q,value:t,invalid:!!W,onChange:e=>T(e.target.value),id:"exampleFormControlTextarea1",rows:10}),(0,y.jsx)(j.C,{invalid:!0,children:2===W?"Aborting might cause some data to be lost, its best to reset after aborting!":"Error generating a response, check your console"}),q.length?q.map(((e,s)=>(0,y.jsxs)(g.C,{color:"dark",shape:"rounded-pill",className:"me-2 mt-3",children:[e/1e3," s"]},"badge-".concat(s,"-").concat(e)))):""]}),(0,y.jsxs)("div",{className:"mb-3 ",children:[(0,y.jsx)(b.u,{color:"primary",disabled:V||J||!t,onClick:ne,children:I?"Stopping...":V?"Waiting...":J?"Streaming...":Q?"Continue":"Send Prompt"}),Q&&!V&&!J&&" or ",!V&&!J&&Q&&(0,y.jsx)(b.u,{color:"secondary",disabled:V||J,onClick:()=>{s((0,k.Z)()),F(!1),G(""),O(null),R(0),M([]),B(!1),H(!1),K(!1),X(!1)},children:"reset"}),V||J?(0,y.jsxs)(u.L,{children:[(0,y.jsx)("strong",{children:"\xa0\xa0Segment time:\xa0"}),(0,y.jsx)(_,{})," seconds"]}):P?(0,y.jsxs)(u.L,{children:[(0,y.jsx)("strong",{children:"\xa0\xa0Generation:\xa0"}),q.reduce(((e,s)=>e+s),0)/1e3," seconds"]}):"",(0,y.jsx)(b.u,{color:"secondary",className:"float-end ms-3",disabled:!V&&!J||I,onClick:()=>F(!0),children:"Stop"}),(0,y.jsx)(b.u,{color:"secondary",className:"float-end",disabled:!V&&!J,onClick:()=>{F(!0),console.log(L),L&&L.abort()},children:"Abort"}),"\xa0\xa0"]}),(0,y.jsx)(p.E,{style:{cursor:"pointer"},checked:E,disabled:V||J,onChange:e=>D(e.target.checked),className:"mt-2",type:"checkbox",id:"autoContinueCheck",label:(0,y.jsx)("span",{style:{cursor:"pointer"},children:"Automatically continue prompt generation when didnt reach EOS"})}),(0,y.jsx)(p.E,{style:{cursor:"pointer"},checked:Y,disabled:V||J,onChange:e=>A(e.target.checked),className:"mt-2",type:"checkbox",id:"onlyNewTokensCheck",label:(0,y.jsx)("span",{style:{cursor:"pointer"},children:"Only return new tokens, if disabled returns response including prompt"})})]}),Z&&(0,y.jsxs)(r.x,{className:"mb-5 ",children:[(0,y.jsxs)(l.b,{children:["Response to requestID ",e,":",(0,y.jsx)(b.u,{color:U?"info":"light",className:"float-end",onClick:()=>z(!U),children:U?"View markdown":"View raw response"})]}),(0,y.jsx)(o.s,{children:U?(0,y.jsx)("span",{className:"markdown-llm",children:Z}):(0,y.jsx)(w.U,{components:te,skipHtml:!0,className:"markdown-llm",children:Z.replace(/ /g,"\xa0")})})]})]})}}}]);
//# sourceMappingURL=184.b61b0cb1.chunk.js.map